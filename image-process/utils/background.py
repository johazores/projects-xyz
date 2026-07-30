"""Optional local background removal using rembg."""

from __future__ import annotations

from pathlib import Path


def remove_background(input_path: Path, output_path: Path, model_name: str) -> Path:
    """Remove an image background and write a transparent PNG."""

    try:
        from rembg import new_session, remove
    except ImportError as exc:
        raise RuntimeError(
            "Background removal requires rembg. "
            "Install it with: pip install -r requirements-background.txt"
        ) from exc

    session = new_session(model_name)
    output = remove(input_path.read_bytes(), session=session)
    output_path.write_bytes(output)
    return output_path
