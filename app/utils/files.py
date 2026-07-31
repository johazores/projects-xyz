"""Local path and output helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
from uuid import uuid4

from app.config import settings
from app.models import MediaOutput


class MediaError(RuntimeError):
    """Readable processing error returned by the API."""


def slugify(value: str, fallback: str = "output") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return (slug or fallback)[:64]


def existing_file(value: str | Path) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    return path


def media_output_dir(media_type: str, project: str | None = None) -> Path:
    base = settings.output_dir
    if project:
        base = base / slugify(project, "project")
    path = base / media_type
    path.mkdir(parents=True, exist_ok=True)
    return path


def unique_path(directory: Path, prefix: str, extension: str) -> Path:
    extension = extension if extension.startswith(".") else f".{extension}"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return directory / f"{slugify(prefix)}-{timestamp}-{uuid4().hex[:6]}{extension}"


def unique_directory(directory: Path, prefix: str) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = directory / f"{slugify(prefix)}-{timestamp}-{uuid4().hex[:6]}"
    path.mkdir(parents=True)
    return path


def output_response(
    media_type: str,
    operation: str,
    path: Path,
    provider: str | None = None,
) -> MediaOutput:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(settings.output_dir)
    except ValueError as exc:
        raise MediaError("Output was created outside the configured output directory.") from exc

    return MediaOutput(
        media_type=media_type,
        operation=operation,
        provider=provider,
        filename=resolved.name,
        output_path=str(resolved),
        output_url=f"/outputs/{relative.as_posix()}",
    )
