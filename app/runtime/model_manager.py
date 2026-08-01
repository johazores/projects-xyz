"""Keeps at most one heavyweight local model active."""

from __future__ import annotations

from threading import RLock
from typing import Any

from app.core.adapters import ModelAdapter, ProgressCallback
from app.core.registry import ModelRegistry


class ModelManager:
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self._active_id: str | None = None
        self._adapter: ModelAdapter | None = None
        self._lock = RLock()

    @property
    def active_id(self) -> str | None:
        return self._active_id

    def run(self, model_id: str, payload: dict[str, Any], progress: ProgressCallback) -> dict[str, Any]:
        with self._lock:
            adapter = self._get(model_id)
            return adapter.run(payload, progress)

    def unload(self) -> None:
        with self._lock:
            if self._adapter is not None:
                self._adapter.unload()
            self._adapter = None
            self._active_id = None

    def _get(self, model_id: str) -> ModelAdapter:
        with self._lock:
            if self._active_id == model_id and self._adapter is not None:
                return self._adapter
            self.unload()
            adapter = self.registry.create(model_id)
            adapter.load()
            self._adapter = adapter
            self._active_id = model_id
            return adapter
