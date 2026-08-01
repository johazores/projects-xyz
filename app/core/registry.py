"""Configuration-backed registry for replaceable local models."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Callable

from app.adapters.bark import BarkAdapter
from app.adapters.faster_whisper import FasterWhisperAdapter
from app.adapters.kokoro import KokoroAdapter
from app.core.adapters import ModelAdapter, ModelSpec
from app.utils.files import MediaError

AdapterFactory = Callable[[ModelSpec], ModelAdapter]

ADAPTER_FACTORIES: dict[str, AdapterFactory] = {
    "bark": BarkAdapter,
    "faster-whisper": FasterWhisperAdapter,
    "kokoro": KokoroAdapter,
}


class ModelRegistry:
    def __init__(self, path: Path):
        self.path = path
        self._specs = self._load(path)

    def list(self) -> list[ModelSpec]:
        return list(self._specs.values())

    def get(self, model_id: str) -> ModelSpec:
        try:
            return self._specs[model_id]
        except KeyError as exc:
            raise MediaError(f"Unknown model: {model_id}") from exc

    def create(self, model_id: str) -> ModelAdapter:
        spec = self.get(model_id)
        if not spec.implemented:
            raise MediaError(f"Model {model_id} is planned but not implemented yet.")
        factory = ADAPTER_FACTORIES.get(spec.adapter)
        if not factory:
            raise MediaError(f"Adapter is not registered: {spec.adapter}")
        return factory(spec)

    def is_available(self, spec: ModelSpec) -> bool:
        return spec.implemented and all(importlib.util.find_spec(name) is not None for name in spec.packages)

    @staticmethod
    def _load(path: Path) -> dict[str, ModelSpec]:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise MediaError(f"Unable to load model configuration: {exc}") from exc
        specs: dict[str, ModelSpec] = {}
        for item in raw.get("models", []):
            spec = ModelSpec(
                id=item["id"], capability=item["capability"], adapter=item["adapter"],
                description=item["description"], implemented=item.get("implemented", False),
                recommended=item.get("recommended", False), vram_gb=item.get("vram_gb"),
                dependency_group=item.get("dependency_group"), packages=tuple(item.get("packages", [])),
                notes=item.get("notes"), options=item.get("options", {}),
            )
            if spec.id in specs:
                raise MediaError(f"Duplicate model id: {spec.id}")
            specs[spec.id] = spec
        return specs
