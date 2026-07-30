"""Dependency-free demo video provider."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from config import VideoConfig


class DemoVideoProvider:
    """Write a request manifest that represents a future asynchronous video job."""

    file_extension = ".json"

    def generate(self, prompt: str, output_path: Path, config: VideoConfig) -> Path:
        if not prompt.strip():
            raise ValueError("A prompt is required.")

        manifest = {
            "status": "demo",
            "provider": "demo",
            "model": config.model,
            "prompt": prompt.strip(),
            "duration_seconds": config.duration_seconds,
            "aspect_ratio": config.aspect_ratio,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "note": (
                "This manifest validates the toolkit workflow. "
                "A real provider will submit a job, poll its status, and download a video."
            ),
        }
        output_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return output_path
