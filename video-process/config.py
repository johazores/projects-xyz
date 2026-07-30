"""Configuration loading for the video project."""

from __future__ import annotations

from dataclasses import dataclass, fields
import json
import os
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class VideoConfig:
    """Runtime settings for video generation."""

    provider: str = "demo"
    model: str = "default"
    output_dir: str = "outputs"
    duration_seconds: int = 5
    aspect_ratio: str = "16:9"
    max_retries: int = 2
    retry_delay_seconds: float = 1.0
    log_level: str = "INFO"
    api_key: str | None = None


def load_config(path: str | Path | None = None) -> VideoConfig:
    """Load defaults, an optional JSON file, and secret environment values."""

    config_path = Path(path or os.getenv("VIDEO_PROCESS_CONFIG", "config.json"))
    values: dict[str, Any] = {}

    if config_path.exists():
        try:
            values = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Unable to read video config: {exc}") from exc

    allowed = {field.name for field in fields(VideoConfig)}
    unknown = sorted(set(values) - allowed)
    if unknown:
        raise ValueError(f"Unknown video config keys: {', '.join(unknown)}")

    values["api_key"] = os.getenv("VIDEO_API_KEY") or values.get("api_key")
    config = VideoConfig(**values)

    if config.duration_seconds <= 0:
        raise ValueError("duration_seconds must be greater than 0.")
    if config.max_retries < 0:
        raise ValueError("max_retries must be 0 or greater.")
    if config.retry_delay_seconds < 0:
        raise ValueError("retry_delay_seconds must be 0 or greater.")
    if ":" not in config.aspect_ratio:
        raise ValueError("aspect_ratio must use a value such as 16:9 or 9:16.")

    return config
