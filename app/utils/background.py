"""Optional local image background removal."""

from __future__ import annotations

from pathlib import Path

from app.utils.files import MediaError


def remove_background(source: Path, destination: Path, model_name: str) -> None:
    try:
        from rembg import new_session, remove
    except ImportError as exc:
        raise MediaError(
            "Background removal is optional. Install it with `pip install -r requirements-local.txt`."
        ) from exc

    session = new_session(model_name)
    destination.write_bytes(remove(source.read_bytes(), session=session))
