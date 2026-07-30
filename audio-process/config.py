"""Configuration loading for the audio project."""

from __future__ import annotations

from dataclasses import dataclass, fields
import json
import os
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class AudioConfig:
    """Runtime settings for audio generation and processing."""

    provider: str = "demo"
    model: str = "suno/bark-small"
    output_dir: str = "outputs"
    sample_rate: int = 24_000
    duration_seconds: float = 3.0
    device: str = "auto"
    max_retries: int = 2
    retry_delay_seconds: float = 1.0
    log_level: str = "INFO"
    api_key: str | None = None


def load_config(path: str | Path | None = None) -> AudioConfig:
    """Load defaults, then an optional JSON file, then secret environment values."""

    config_path = Path(path or os.getenv("AUDIO_PROCESS_CONFIG", "config.json"))
    values: dict[str, Any] = {}

    if config_path.exists():
        try:
            values = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Unable to read audio config: {exc}") from exc

    allowed = {field.name for field in fields(AudioConfig)}
    unknown = sorted(set(values) - allowed)
    if unknown:
        raise ValueError(f"Unknown audio config keys: {', '.join(unknown)}")

    values["api_key"] = os.getenv("AUDIO_API_KEY") or values.get("api_key")
    config = AudioConfig(**values)

    if config.max_retries < 0:
        raise ValueError("max_retries must be 0 or greater.")
    if config.retry_delay_seconds < 0:
        raise ValueError("retry_delay_seconds must be 0 or greater.")
    if config.sample_rate <= 0:
        raise ValueError("sample_rate must be greater than 0.")
    if config.duration_seconds <= 0:
        raise ValueError("duration_seconds must be greater than 0.")

    return config
