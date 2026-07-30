"""Shared response building for media services."""

from __future__ import annotations

from pathlib import Path

from app.config import Settings
from app.models import MediaOutput


def build_output(
    media_type: str,
    provider: str,
    output_path: Path,
    settings: Settings,
) -> MediaOutput:
    """Build a stable API response for a generated local file."""

    relative_path = output_path.relative_to(settings.output_dir).as_posix()
    return MediaOutput(
        media_type=media_type,
        provider=provider,
        filename=output_path.name,
        output_path=str(output_path),
        output_url=f"/outputs/{relative_path}",
    )
