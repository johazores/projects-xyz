"""Reusable music and sound-effect prompt presets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.utils.files import MediaError


class AudioPresetStore:
    def __init__(self, path: Path):
        self.path = path

    def list(self) -> dict[str, dict[str, Any]]:
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise MediaError(f"Unable to load audio presets: {exc}") from exc
        if not isinstance(value, dict):
            raise MediaError("Audio presets must be a JSON object.")
        return value

    def apply(self, model_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        preset_name = str(payload.get("preset") or "").strip()
        if not preset_name:
            return dict(payload)
        presets = self.list()
        preset = presets.get(preset_name)
        if not isinstance(preset, dict):
            raise MediaError(f"Unknown audio preset: {preset_name}. Available: {', '.join(sorted(presets))}")
        capability = "music" if model_id.startswith("music.") else "sound-effect"
        if preset.get("kind") != capability:
            raise MediaError(f"Preset {preset_name} is not a {capability} preset.")
        result = dict(payload)
        prompt = str(result.get("prompt", "")).strip()
        prefix = str(preset.get("prompt_prefix", "")).strip()
        suffix = str(preset.get("prompt_suffix", "")).strip()
        result["prompt"] = " ".join(value for value in (prefix, prompt, suffix) if value)
        for key, value in dict(preset.get("defaults") or {}).items():
            result.setdefault(key, value)
        result["applied_preset"] = preset_name
        return result
