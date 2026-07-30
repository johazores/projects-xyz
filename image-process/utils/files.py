"""Output path helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
from uuid import uuid4


def ensure_directory(path: str | Path) -> Path:
    """Create a directory when needed and return it."""

    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def slugify(value: str, fallback: str = "output") -> str:
    """Create a short filename-safe value."""

    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return (slug or fallback)[:48]


def create_output_path(
    output_dir: str | Path,
    prompt: str,
    extension: str,
    prefix: str = "image",
) -> Path:
    """Build a unique output path using the prompt and current UTC time."""

    extension = extension if extension.startswith(".") else f".{extension}"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    suffix = uuid4().hex[:6]
    filename = f"{prefix}-{slugify(prompt)}-{timestamp}-{suffix}{extension}"
    return ensure_directory(output_dir) / filename
