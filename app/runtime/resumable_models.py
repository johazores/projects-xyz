"""Model-manager proxy that reuses valid checkpoints during workflow resume."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from app.runtime.project_store import ProjectStore


class ResumableModelManager:
    def __init__(self, manager: Any, projects: ProjectStore, run_id: str):
        self.manager = manager
        self.projects = projects
        self.run_id = run_id
        self.registry = manager.registry

    @property
    def active_id(self) -> str | None:
        return self.manager.active_id

    def run(self, model_id: str, payload: dict[str, Any], progress: Any) -> dict[str, Any]:
        serialized = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
        payload_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        step_id = f"{model_id}-{payload_hash[:20]}"
        reusable = self.projects.reusable_step(self.run_id, step_id)
        if reusable is not None:
            progress(100, f"Reusing completed {model_id} checkpoint")
            reusable.setdefault("checkpoint_reused", True)
            return reusable

        self.projects.step_start(self.run_id, step_id, model_id, payload_hash)
        try:
            result = self.manager.run(model_id, payload, progress)
        except Exception as exc:
            self.projects.step_fail(self.run_id, step_id, str(exc))
            raise
        self.projects.step_complete(self.run_id, step_id, result)
        return result

    def unload(self) -> None:
        self.manager.unload()
