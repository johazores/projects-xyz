"""Provider contract for image generation."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from config import ImageConfig


class ImageProvider(Protocol):
    """Minimal interface implemented by image generation providers."""

    file_extension: str

    def generate(
        self,
        prompt: str,
        negative_prompt: str | None,
        output_path: Path,
        config: ImageConfig,
    ) -> Path:
        """Generate an image file and return its path."""
