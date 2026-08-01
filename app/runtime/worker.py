"""One local background worker for serialized GPU jobs."""

from __future__ import annotations

from queue import Empty, Queue
from threading import Event, Thread
from typing import Any

from app.runtime.job_store import JobStore
from app.runtime.model_manager import ModelManager
from app.workflows import youtube


class JobCancelled(RuntimeError):
    pass


class JobWorker:
    def __init__(self, store: JobStore, models: ModelManager):
        self.store = store
        self.models = models
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
        job = self.store.create(kind, target, payload)
        self.queue.put(job.id)
        return job

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
            self.store.update(job_id, status="cancelled", progress=100, message="Cancelled", finished=True)
            return
        job = self.store.update(job_id, status="running", progress=1, message="Starting", started=True)

        def progress(value: int, message: str) -> None:
            if self.store.cancel_requested(job_id):
                raise JobCancelled("Job cancellation requested.")
            self.store.update(job_id, progress=max(1, min(99, int(value))), message=message)

        try:
            if job.kind == "model":
                result = self.models.run(job.target, job.payload, progress)
            else:
                result = youtube.run(job.target, job.payload, self.models, progress)
            self.store.update(job_id, status="completed", progress=100, message="Completed", result=result, finished=True)
        except JobCancelled as exc:
            self.store.update(job_id, status="cancelled", progress=100, message="Cancelled", error=str(exc), finished=True)
        except Exception as exc:
            self.store.update(job_id, status="failed", progress=100, message="Failed", error=str(exc), finished=True)
