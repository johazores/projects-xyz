"""Video API integration."""

from __future__ import annotations

from app.config import Settings
from app.models import GenerateRequest, MediaOutput
from app.services.common import build_output
from app.services.runner import run_cli


def generate_video(request: GenerateRequest, settings: Settings) -> MediaOutput:
    """Generate a video artifact through the existing video project."""

    output_path = run_cli(
        settings.video_dir,
        [
            "generate",
            "--prompt",
            request.prompt,
            "--provider",
            request.provider,
            "--output-dir",
            str(settings.output_dir / "video"),
        ],
        settings.process_timeout_seconds,
    )
    return build_output("video", request.provider, output_path, settings)
