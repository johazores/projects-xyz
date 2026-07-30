"""Small reusable prompt presets for common content and game assets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PRESET_PATH = Path(__file__).resolve().parents[1] / "presets.json"


def load_presets(path: str | Path | None = None) -> dict[str, dict[str, str]]:
    """Load prompt presets from JSON."""

    preset_path = Path(path) if path else PRESET_PATH
    try:
        data: dict[str, Any] = json.loads(preset_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to read image presets: {exc}") from exc

    presets: dict[str, dict[str, str]] = {}
    for name, values in data.items():
        if not isinstance(values, dict) or "template" not in values:
            raise ValueError(f"Invalid image preset: {name}")
        presets[name] = {
            "template": str(values["template"]),
            "negative_prompt": str(values.get("negative_prompt", "")),
        }
    return presets


def apply_preset(
    prompt: str,
    negative_prompt: str | None,
    preset_name: str | None,
) -> tuple[str, str | None]:
    """Apply one preset while preserving explicit negative prompts."""

    if not preset_name:
        return prompt, negative_prompt

    presets = load_presets()
    if preset_name not in presets:
        available = ", ".join(sorted(presets))
        raise ValueError(f"Unknown image preset: {preset_name}. Available presets: {available}.")

    preset = presets[preset_name]
    prepared_prompt = preset["template"].format(prompt=prompt.strip())
    prepared_negative = negative_prompt or preset["negative_prompt"] or None
    return prepared_prompt, prepared_negative
