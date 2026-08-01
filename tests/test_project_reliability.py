from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from app.runtime.audio_presets import AudioPresetStore
from app.runtime.cleanup import cleanup
from app.runtime.project_store import ProjectStore
from app.runtime.readiness import readiness_snapshot
from app.runtime.resumable_models import ResumableModelManager
from app.runtime.worker import JobWorker
from app.utils.files import MediaError


class FakeRegistry:
    def __init__(self) -> None:
        self.spec = SimpleNamespace(id="music.test", implemented=True)

    def list(self) -> list[object]:
        return [self.spec]

    def get(self, _: str) -> object:
        return self.spec

    def is_available(self, _: object) -> bool:
        return True


class FakeManager:
    def __init__(self, output: Path) -> None:
        self.registry = FakeRegistry()
        self.active_id = None
        self.calls = 0
        self.output = output

    def run(self, _: str, payload: dict, progress: object) -> dict:
        self.calls += 1
        self.output.write_text("ok", encoding="utf-8")
        progress(50, "running")
        return {"output_path": str(self.output), "prompt": payload.get("prompt")}

    def unload(self) -> None:
        return None


class FakeJob:
    def __init__(self, job_id: str, kind: str, target: str, payload: dict) -> None:
        self.id = job_id
        self.kind = kind
        self.target = target
        self.payload = payload
        self.status = "queued"


class FakeJobStore:
    def __init__(self) -> None:
        self.jobs: dict[str, FakeJob] = {}
        self.sequence = 0

    def create(self, kind: str, target: str, payload: dict) -> FakeJob:
        self.sequence += 1
        job = FakeJob(str(self.sequence), kind, target, payload)
        self.jobs[job.id] = job
        return job

    def get(self, job_id: str) -> FakeJob:
        return self.jobs[job_id]

    def request_cancel(self, job_id: str) -> FakeJob:
        self.jobs[job_id].cancel_requested = True
        return self.jobs[job_id]

    def cancel_requested(self, job_id: str) -> bool:
        return bool(getattr(self.jobs[job_id], "cancel_requested", False))

    def update(self, job_id: str, **values) -> FakeJob:
        job = self.jobs[job_id]
        for key, value in values.items():
            if key in {"started", "finished"}:
                continue
            if value is not None:
                setattr(job, key, value)
        return job

    def recover_pending(self) -> list[str]:
        return []


class ProjectReliabilityTests(unittest.TestCase):
    def test_checkpoint_reuse_requires_existing_artifacts(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            projects = ProjectStore(root / "projects")
            run = projects.create("youtube.test", {"project": "demo"})
            artifact = root / "output.txt"
            manager = FakeManager(artifact)
            proxy = ResumableModelManager(manager, projects, str(run["id"]))

            proxy.run("music.test", {"prompt": "hello"}, lambda *_: None)
            reused = proxy.run("music.test", {"prompt": "hello"}, lambda *_: None)
            self.assertEqual(manager.calls, 1)
            self.assertTrue(reused["checkpoint_reused"])

            artifact.unlink()
            proxy.run("music.test", {"prompt": "hello"}, lambda *_: None)
            self.assertEqual(manager.calls, 2)

    def test_cleanup_is_dry_run_first_and_protects_active_projects(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "outputs"
            data = root / "data"
            cache = root / "cache"
            output.mkdir()
            data.mkdir()
            cache.mkdir()
            projects = ProjectStore(data / "projects")
            run = projects.create("youtube.test", {"project": "demo"})
            project_dir = output / "demo"
            project_dir.mkdir()
            (project_dir / "asset.bin").write_bytes(b"content")
            settings = SimpleNamespace(
                output_dir=output,
                data_dir=data,
                model_cache_dir=cache,
                min_disk_free_gb=0,
            )

            projects.start(str(run["id"]))
            with self.assertRaises(MediaError):
                cleanup(
                    settings=settings,
                    projects=projects,
                    project="demo",
                    older_than_days=None,
                    include_project_runs=False,
                    include_model_cache=False,
                    dry_run=True,
                    confirm=False,
                )

            projects.fail(str(run["id"]), "expected test failure")
            preview = cleanup(
                settings=settings,
                projects=projects,
                project="demo",
                older_than_days=None,
                include_project_runs=True,
                include_model_cache=False,
                dry_run=True,
                confirm=False,
            )
            self.assertTrue(project_dir.exists())
            self.assertIn(str(project_dir), preview["paths"])

            cleanup(
                settings=settings,
                projects=projects,
                project="demo",
                older_than_days=None,
                include_project_runs=True,
                include_model_cache=False,
                dry_run=False,
                confirm=True,
            )
            self.assertFalse(project_dir.exists())

    def test_model_cache_cleanup_preserves_configured_root(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "outputs"
            data = root / "data"
            cache = root / "cache"
            output.mkdir()
            data.mkdir()
            cache.mkdir()
            (cache / "model.bin").write_bytes(b"model")
            settings = SimpleNamespace(
                output_dir=output,
                data_dir=data,
                model_cache_dir=cache,
                min_disk_free_gb=0,
            )
            projects = ProjectStore(data / "projects")

            cleanup(
                settings=settings,
                projects=projects,
                project=None,
                older_than_days=None,
                include_project_runs=False,
                include_model_cache=True,
                dry_run=False,
                confirm=True,
            )
            self.assertTrue(cache.exists())
            self.assertEqual(list(cache.iterdir()), [])

    def test_audio_presets_validate_capability(self) -> None:
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "audio-presets.json"
            path.write_text(
                json.dumps(
                    {
                        "technology": {
                            "kind": "music",
                            "prompt_prefix": "modern",
                            "prompt_suffix": "clean",
                            "defaults": {"bpm": 90},
                        }
                    }
                ),
                encoding="utf-8",
            )
            presets = AudioPresetStore(path)
            applied = presets.apply(
                "music.ace-step-1.5",
                {"prompt": "studio", "preset": "technology"},
            )
            self.assertEqual(applied["prompt"], "modern studio clean")
            self.assertEqual(applied["bpm"], 90)
            with self.assertRaises(MediaError):
                presets.apply(
                    "audio.stable-audio-small-sfx",
                    {"prompt": "click", "preset": "technology"},
                )

    def test_resume_uses_the_same_project_run(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            presets_path = root / "audio-presets.json"
            presets_path.write_text("{}", encoding="utf-8")
            projects = ProjectStore(root / "projects")
            worker = JobWorker(
                FakeJobStore(),
                FakeManager(root / "output.txt"),
                projects,
                AudioPresetStore(presets_path),
            )
            job = worker.submit(
                "workflow",
                "youtube.test",
                {"project": "resume-demo", "prompt": "hello"},
            )
            run_id = str(job.payload["_run_id"])
            projects.fail(run_id, "expected")
            resumed = worker.resume(run_id)
            self.assertEqual(resumed.payload["_run_id"], run_id)
            self.assertEqual(projects.get(run_id)["status"], "queued")

    def test_prestart_cancellation_closes_project_run(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            presets_path = root / "audio-presets.json"
            presets_path.write_text("{}", encoding="utf-8")
            store = FakeJobStore()
            projects = ProjectStore(root / "projects")
            worker = JobWorker(
                store,
                FakeManager(root / "output.txt"),
                projects,
                AudioPresetStore(presets_path),
            )
            job = worker.submit("workflow", "youtube.test", {"project": "cancel-demo"})
            run_id = str(job.payload["_run_id"])
            worker.cancel(job.id)
            worker._run(job.id)
            self.assertEqual(projects.get(run_id)["status"], "cancelled")
            self.assertNotIn("cancel-demo", projects.active_projects())

    def test_readiness_includes_storage_and_models(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "outputs"
            data = root / "data"
            output.mkdir()
            data.mkdir()
            settings = SimpleNamespace(
                output_dir=output,
                data_dir=data,
                model_cache_dir=None,
                min_disk_free_gb=0,
            )
            snapshot = readiness_snapshot(settings, FakeRegistry())
            self.assertIn("disk_headroom", snapshot["checks"])
            self.assertEqual(snapshot["checks"]["models"]["available"], 1)


if __name__ == "__main__":
    unittest.main()
