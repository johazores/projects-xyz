"""Configuration-backed registry for replaceable local models."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
from typing import Callable

from app.adapters.ace_step import AceStepAdapter
from app.adapters.bark import BarkAdapter
from app.adapters.birefnet import BiRefNetAdapter
from app.adapters.chatterbox import ChatterboxAdapter
from app.adapters.faster_whisper import FasterWhisperAdapter
from app.adapters.florence import FlorenceAdapter
from app.adapters.kokoro import KokoroAdapter
from app.adapters.ltx_video import LtxVideoAdapter
from app.adapters.realesrgan import RealEsrganNcnnAdapter
from app.adapters.sana import SanaAdapter
from app.adapters.sdxl_inpaint import SdxlInpaintAdapter
from app.adapters.stable_audio import StableAudioCliAdapter
from app.core.adapters import ModelAdapter, ModelSpec
from app.utils.files import MediaError

AdapterFactory = Callable[[ModelSpec], ModelAdapter]

ADAPTER_FACTORIES: dict[str, AdapterFactory] = {
    "ace-step": AceStepAdapter,
    "bark": BarkAdapter,
    "birefnet": BiRefNetAdapter,
    "chatterbox": ChatterboxAdapter,
    "faster-whisper": FasterWhisperAdapter,
    "florence": FlorenceAdapter,
    "kokoro": KokoroAdapter,
    "ltx-video": LtxVideoAdapter,
    "realesrgan-ncnn": RealEsrganNcnnAdapter,
    "sana": SanaAdapter,
    "sdxl-inpaint": SdxlInpaintAdapter,
    "stable-audio-cli": StableAudioCliAdapter,
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
        if not spec.implemented:
            return False
        packages_available = all(importlib.util.find_spec(name) is not None for name in spec.packages)
        availability = spec.options.get("availability")
        if availability == "packages-or-external":
            return packages_available or self._external_repo_available(spec)
        if availability == "configured-http":
            return self._http_configured(spec)
        return packages_available and self._executable_available(spec)

    @staticmethod
    def _http_configured(spec: ModelSpec) -> bool:
        env_name = str(spec.options.get("url_env", ""))
        return bool(env_name and os.getenv(env_name, "").strip())

    @staticmethod
    def _external_repo_available(spec: ModelSpec) -> bool:
        env_name = str(spec.options.get("external_repo_env", ""))
        entrypoint = str(spec.options.get("external_entrypoint", "inference.py"))
        value = os.getenv(env_name) if env_name else None
        return bool(value and (Path(value).expanduser() / entrypoint).is_file())

    @staticmethod
    def _executable_available(spec: ModelSpec) -> bool:
        if not spec.executable:
            return True
        env_name = str(spec.options.get("executable_env", ""))
        configured = os.getenv(env_name) if env_name else None
        for candidate in (configured, spec.options.get("executable"), spec.executable):
            if not candidate:
                continue
            path = Path(str(candidate)).expanduser()
            if path.is_file() or shutil.which(str(candidate)):
                return True
        return False

    @staticmethod
    def _load(path: Path) -> dict[str, ModelSpec]:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise MediaError(f"Unable to load model configuration: {exc}") from exc
        specs: dict[str, ModelSpec] = {}
        for item in raw.get("models", []):
            spec = ModelSpec(
                id=item["id"],
                capability=item["capability"],
                adapter=item["adapter"],
                description=item["description"],
                implemented=item.get("implemented", False),
                recommended=item.get("recommended", False),
                vram_gb=item.get("vram_gb"),
                dependency_group=item.get("dependency_group"),
                packages=tuple(item.get("packages", [])),
                executable=item.get("executable"),
                notes=item.get("notes"),
                options=item.get("options", {}),
            )
            if spec.id in specs:
                raise MediaError(f"Duplicate model id: {spec.id}")
            specs[spec.id] = spec
        return specs
