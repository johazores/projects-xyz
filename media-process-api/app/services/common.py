"""Shared output path and response helpers."""

from __future__ import annotations

from pathlib import Path
import re

from app.config import Settings
from app.models import MediaOutput


def output_directory(
    settings: Settings,
    media_type: str,
    project: str | None = None,
) -> Path:
    """Return an organized API output folder."""

    directory = settings.output_dir
    if project:
        slug = re.sub(r"[^a-z0-9]+", "-", project.lower()).strip("-")[:80]
        if not slug:
            raise ValueError("project must contain at least one letter or number.")
        directory /= slug
    return directory / media_type


def build_output(
    media_type: str,
    output_path: Path,
    settings: Settings,
    *,
    operation: str,
    provider: str | None = None,
) -> MediaOutput:
    """Build a stable API response for a generated local file."""

    relative_path = output_path.relative_to(settings.output_dir).as_posix()
    return MediaOutput(
        media_type=media_type,
        operation=operation,
        provider=provider,
        filename=output_path.name,
        output_path=str(output_path),
        output_url=f"/outputs/{relative_path}",
    )
