"""Provider contract for audio generation."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from config import AudioConfig


class AudioProvider(Protocol):
    """Minimal interface implemented by audio generation providers."""

    file_extension: str

    def generate(self, prompt: str, output_path: Path, config: AudioConfig) -> Path:
        """Generate an audio file and return its path."""
