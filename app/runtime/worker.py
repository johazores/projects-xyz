"""One local background worker for serialized GPU jobs."""

from __future__ import annotations

from copy import deepcopy
from queue import Empty, Queue
from threading import Event, Thread
from typing import Any

from app.runtime.audio_presets import AudioPresetStore
from app.runtime.job_store import JobStore
from app.runtime.model_manager import ModelManager
from app.runtime.project_store import ProjectStore
from app.runtime.resumable_models import ResumableModelManager
from app.workflows import youtube


class JobCancelled(RuntimeError):
    pass


class JobWorker:
    def __init__(
        self,
        store: JobStore,
        models: ModelManager,
        projects: ProjectStore,
        audio_presets: AudioPresetStore,
    ):
        self.store = store
        self.models = models
        self.projects = projects
        self.audio_presets = audio_presets
        self.queue: Queue[str] = Queue()
        self.stop_event = Event()
        self.thread: Thread | None = None

    @property
    def running(self) -> bool:
        return bool(self.thread and self.thread.is_alive())

    def start(self) -> None:
        if self.running:
            return
        self.stop_event.clear()
        for job_id in self.store.recover_pending():
            self.queue.put(job_id)
        self.thread = Thread(target=self._loop, name="local-ai-worker", daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=5)
        if not self.running:
            self.models.unload()

    def submit(self, kind: str, target: str, payload: dict[str, Any]):
        prepared = deepcopy(payload)
        if kind == "workflow":
            run_id = str(prepared.pop("_run_id", "")).strip()
            if run_id:
                self.projects.prepare_resume(run_id)
            else:
                run_id = str(self.projects.create(target, prepared)["id"])
            prepared["_run_id"] = run_id
        job = self.store.create(kind, target, prepared)
        if kind == "workflow":
            self.projects.attach_job(str(prepared["_run_id"]), job.id)
        self.queue.put(job.id)
        return job

    def resume(self, run_id: str):
        record = self.projects.get(run_id)
        return self.submit(
            "workflow",
            str(record["workflow"]),
            {**dict(record["payload"]), "_run_id": run_id},
        )

    def cancel(self, job_id: str):
        return self.store.request_cancel(job_id)

    def _loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                job_id = self.queue.get(timeout=0.25)
            except Empty:
                continue
            try:
                self._run(job_id)
            finally:
                self.queue.task_done()

    def _run(self, job_id: str) -> None:
        if self.store.cancel_requested(job_id):
            job = self.store.get(job_id)
            run_id = str(job.payload.get("_run_id", "")) if job.kind == "workflow" else ""
            if run_id:
                self.projects.fail(run_id, "Job cancellation requested before start.", cancelled=True)
            self.store.update(job_id, status="cancelled", progress=100, message="Cancelled", finished=True)
            return
        job = self.store.update(job_id, status="running", progress=1, message="Starting", started=True)
        run_id = str(job.payload.get("_run_id", "")) if job.kind == "workflow" else ""
        if run_id:
            self.projects.start(run_id)

        def progress(value: int, message: str) -> None:
            if self.store.cancel_requested(job_id):
                raise JobCancelled("Job cancellation requested.")
            self.store.update(job_id, progress=max(1, min(99, int(value))), message=message)

        try:
            if job.kind == "model":
                model_payload = self._prepare_model_payload(job.target, job.payload)
                result = self.models.run(job.target, model_payload, progress)
            else:
                workflow_payload = self._prepare_workflow_payload(job.target, job.payload)
                workflow_payload.pop("_run_id", None)
                manager = ResumableModelManager(self.models, self.projects, run_id)
                result = youtube.run(job.target, workflow_payload, manager, progress)
                result["project_run_id"] = run_id
                self.projects.complete(run_id, result)
            self.store.update(job_id, status="completed", progress=100, message="Completed", result=result, finished=True)
        except JobCancelled as exc:
            if run_id:
                self.projects.fail(run_id, str(exc), cancelled=True)
            self.store.update(job_id, status="cancelled", progress=100, message="Cancelled", error=str(exc), finished=True)
        except Exception as exc:
            if run_id:
                self.projects.fail(run_id, str(exc))
            self.store.update(job_id, status="failed", progress=100, message="Failed", error=str(exc), finished=True)

    def _prepare_model_payload(self, target: str, payload: dict[str, Any]) -> dict[str, Any]:
        if payload.get("preset") and (
            target.startswith("music.") or target.startswith("audio.stable-audio")
        ):
            return self.audio_presets.apply(target, payload)
        return dict(payload)

    def _prepare_workflow_payload(self, target: str, payload: dict[str, Any]) -> dict[str, Any]:
        prepared = deepcopy(payload)
        if target == "youtube.ai-short":
            music_preset = prepared.get("music_preset")
            if music_preset and prepared.get("music_prompt"):
                music = self.audio_presets.apply(
                    str(prepared.get("music_model", "music.ace-step-1.5")),
                    {"prompt": prepared["music_prompt"], "preset": music_preset},
                )
                prepared["music_prompt"] = music["prompt"]
            for scene in prepared.get("scenes") or []:
                if scene.get("sfx_preset") and scene.get("sfx_prompt"):
                    effect = self.audio_presets.apply(
                        str(prepared.get("sfx_model", "audio.stable-audio-small-sfx")),
                        {"prompt": scene["sfx_prompt"], "preset": scene["sfx_preset"]},
                    )
                    scene["sfx_prompt"] = effect["prompt"]
        elif target == "youtube.podcast" and prepared.get("music_preset") and prepared.get("music_prompt"):
            music = self.audio_presets.apply(
                str(prepared.get("music_model", "music.ace-step-1.5")),
                {"prompt": prepared["music_prompt"], "preset": prepared["music_preset"]},
            )
            prepared["music_prompt"] = music["prompt"]
        return prepared
