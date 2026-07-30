"""Provider contract for video generation."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from config import VideoConfig


class VideoProvider(Protocol):
    """Minimal interface implemented by video generation providers."""

    file_extension: str

    def generate(self, prompt: str, output_path: Path, config: VideoConfig) -> Path:
        """Generate a video or generation artifact and return its path."""
