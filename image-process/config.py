"""Configuration loading for the image project."""

from __future__ import annotations

from dataclasses import dataclass, fields
import json
import os
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ImageConfig:
    """Runtime settings for image generation."""

    provider: str = "demo"
    model: str = "default"
    output_dir: str = "outputs"
    width: int = 1024
    height: int = 1024
    max_retries: int = 2
    retry_delay_seconds: float = 1.0
    log_level: str = "INFO"
    api_key: str | None = None


def load_config(path: str | Path | None = None) -> ImageConfig:
    """Load defaults, an optional JSON file, and secret environment values."""

    config_path = Path(path or os.getenv("IMAGE_PROCESS_CONFIG", "config.json"))
    values: dict[str, Any] = {}

    if config_path.exists():
        try:
            values = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Unable to read image config: {exc}") from exc

    allowed = {field.name for field in fields(ImageConfig)}
    unknown = sorted(set(values) - allowed)
    if unknown:
        raise ValueError(f"Unknown image config keys: {', '.join(unknown)}")

    values["api_key"] = os.getenv("IMAGE_API_KEY") or values.get("api_key")
    config = ImageConfig(**values)

    if config.width <= 0 or config.height <= 0:
        raise ValueError("width and height must be greater than 0.")
    if config.max_retries < 0:
        raise ValueError("max_retries must be 0 or greater.")
    if config.retry_delay_seconds < 0:
        raise ValueError("retry_delay_seconds must be 0 or greater.")

    return config
