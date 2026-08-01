"""Durable local project workflow runs and reusable model checkpoints."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
from threading import RLock
from typing import Any
from uuid import uuid4

from app.utils.files import MediaError, slugify

_FINAL_STATUSES = {"completed", "failed", "cancelled"}
_ACTIVE_STATUSES = {"queued", "running"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProjectStore:
    def __init__(self, directory: Path):
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()

    def create(self, workflow: str, payload: dict[str, Any]) -> dict[str, Any]:
        run_id = uuid4().hex
        timestamp = _now()
        record = {
            "id": run_id,
            "project": slugify(str(payload.get("project") or "default"), "default"),
            "workflow": workflow,
            "status": "queued",
            "payload": deepcopy(payload),
            "steps": {},
            "job_ids": [],
            "result": None,
            "error": None,
            "created_at": timestamp,
            "updated_at": timestamp,
            "started_at": None,
            "finished_at": None,
        }
        self._write(record)
        return deepcopy(record)

    def get(self, run_id: str) -> dict[str, Any]:
        path = self._path(run_id)
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise MediaError(f"Project run not found: {run_id}") from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise MediaError(f"Unable to read project run {run_id}: {exc}") from exc
        return value

    def list(self, *, project: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        project_slug = slugify(project, "default") if project else None
        records: list[dict[str, Any]] = []
        for path in self.directory.glob("*.json"):
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if project_slug and record.get("project") != project_slug:
                continue
            records.append(record)
        records.sort(key=lambda item: str(item.get("created_at", "")), reverse=True)
        return records[: max(1, min(500, limit))]

    def attach_job(self, run_id: str, job_id: str) -> dict[str, Any]:
        def update(record: dict[str, Any]) -> None:
            jobs = record.setdefault("job_ids", [])
            if job_id not in jobs:
                jobs.append(job_id)
            record["status"] = "queued"
            record["error"] = None
            record["finished_at"] = None

        return self._mutate(run_id, update)

    def start(self, run_id: str) -> dict[str, Any]:
        def update(record: dict[str, Any]) -> None:
            record["status"] = "running"
            record["started_at"] = record.get("started_at") or _now()
            record["finished_at"] = None
            record["error"] = None

        return self._mutate(run_id, update)

    def complete(self, run_id: str, result: dict[str, Any]) -> dict[str, Any]:
        def update(record: dict[str, Any]) -> None:
            record["status"] = "completed"
            record["result"] = result
            record["error"] = None
            record["finished_at"] = _now()

        return self._mutate(run_id, update)

    def fail(self, run_id: str, error: str, *, cancelled: bool = False) -> dict[str, Any]:
        def update(record: dict[str, Any]) -> None:
            record["status"] = "cancelled" if cancelled else "failed"
            record["error"] = error
            record["finished_at"] = _now()

        return self._mutate(run_id, update)

    def prepare_resume(self, run_id: str) -> dict[str, Any]:
        record = self.get(run_id)
        if record.get("status") in _ACTIVE_STATUSES:
            raise MediaError("An active project run cannot be resumed.")
        if record.get("status") not in _FINAL_STATUSES:
            raise MediaError(f"Project run cannot be resumed from status {record.get('status')}.")

        def update(value: dict[str, Any]) -> None:
            value["status"] = "queued"
            value["error"] = None
            value["result"] = None
            value["finished_at"] = None

        return self._mutate(run_id, update)

    def active_projects(self) -> set[str]:
        return {
            str(record.get("project"))
            for record in self.list(limit=500)
            if record.get("status") in _ACTIVE_STATUSES
        }

    def step_start(self, run_id: str, step_id: str, model_id: str, payload_hash: str) -> None:
        def update(record: dict[str, Any]) -> None:
            record.setdefault("steps", {})[step_id] = {
                "id": step_id,
                "model": model_id,
                "payload_hash": payload_hash,
                "status": "running",
                "result": None,
                "error": None,
                "started_at": _now(),
                "finished_at": None,
            }

        self._mutate(run_id, update)

    def step_complete(self, run_id: str, step_id: str, result: dict[str, Any]) -> None:
        def update(record: dict[str, Any]) -> None:
            step = record.setdefault("steps", {}).setdefault(step_id, {"id": step_id})
            step.update({"status": "completed", "result": result, "error": None, "finished_at": _now()})

        self._mutate(run_id, update)

    def step_fail(self, run_id: str, step_id: str, error: str) -> None:
        def update(record: dict[str, Any]) -> None:
            step = record.setdefault("steps", {}).setdefault(step_id, {"id": step_id})
            step.update({"status": "failed", "error": error, "finished_at": _now()})

        self._mutate(run_id, update)

    def reusable_step(self, run_id: str, step_id: str) -> dict[str, Any] | None:
        step = self.get(run_id).get("steps", {}).get(step_id)
        if not step or step.get("status") != "completed":
            return None
        result = step.get("result")
        if not isinstance(result, dict) or not _result_artifacts_exist(result):
            return None
        return deepcopy(result)

    def delete_record(self, run_id: str) -> None:
        with self._lock:
            self._path(run_id).unlink(missing_ok=True)

    def _mutate(self, run_id: str, callback: Any) -> dict[str, Any]:
        with self._lock:
            record = self.get(run_id)
            callback(record)
            record["updated_at"] = _now()
            self._write(record)
            return deepcopy(record)

    def _write(self, record: dict[str, Any]) -> None:
        with self._lock:
            path = self._path(str(record["id"]))
            temporary = path.with_suffix(".json.tmp")
            temporary.write_text(json.dumps(record, indent=2, default=str), encoding="utf-8")
            temporary.replace(path)

    def _path(self, run_id: str) -> Path:
        if not run_id or any(character not in "0123456789abcdef" for character in run_id.lower()):
            raise MediaError("Invalid project run id.")
        return self.directory / f"{run_id}.json"


def _result_artifacts_exist(value: Any) -> bool:
    paths: list[Path] = []

    def visit(item: Any, key: str | None = None) -> None:
        if isinstance(item, dict):
            for child_key, child in item.items():
                visit(child, str(child_key))
        elif isinstance(item, list):
            for child in item:
                visit(child, key)
        elif isinstance(item, str) and key and (key.endswith("_path") or key == "output_path"):
            paths.append(Path(item).expanduser())

    visit(value)
    return all(path.is_file() or path.is_dir() for path in paths)
