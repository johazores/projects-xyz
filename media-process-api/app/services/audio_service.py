"""Audio API integration."""

from __future__ import annotations

from app.config import Settings
from app.models import GenerateRequest, MediaOutput
from app.services.common import build_output
from app.services.runner import run_cli


def generate_audio(request: GenerateRequest, settings: Settings) -> MediaOutput:
    """Generate audio through the existing audio project."""

    output_dir = settings.output_dir / "audio"
    output_path = run_cli(
        settings.audio_dir,
        [
            "generate",
            "--prompt",
            request.prompt,
            "--provider",
            request.provider,
            "--output-dir",
            str(output_dir),
        ],
        settings.process_timeout_seconds,
    )
    return build_output("audio", request.provider, output_path, settings)
