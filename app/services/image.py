"""Image preset helpers shared by queued model routes."""

from __future__ import annotations

import json

from app.config import settings
from app.utils.files import MediaError


def list_presets() -> dict[str, dict[str, str]]:
    try:
        value = json.loads(settings.presets_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MediaError(f"Unable to load presets: {exc}") from exc
    return value


def apply_preset(
    prompt: str,
    negative_prompt: str | None,
    preset_name: str | None,
) -> tuple[str, str | None]:
    if not preset_name:
        return prompt.strip(), negative_prompt

    presets = list_presets()
    preset = presets.get(preset_name)
    if not preset:
        raise MediaError(
            f"Unknown preset: {preset_name}. Available: {', '.join(sorted(presets))}"
        )
    combined_prompt = f"{preset.get('prefix', '').strip()} {prompt.strip()}".strip()
    preset_negative = preset.get("negative", "").strip()
    combined_negative = ", ".join(
        value for value in (negative_prompt, preset_negative) if value
    ) or None
    return combined_prompt, combined_negative
