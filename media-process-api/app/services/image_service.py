"""Image API integration."""

from __future__ import annotations

from app.config import Settings
from app.models import ImageGenerateRequest, MediaOutput
from app.services.common import build_output
from app.services.runner import run_cli


def generate_image(request: ImageGenerateRequest, settings: Settings) -> MediaOutput:
    """Generate an image through the existing image project."""

    arguments = [
        "generate",
        "--prompt",
        request.prompt,
        "--provider",
        request.provider,
        "--output-dir",
        str(settings.output_dir / "image"),
    ]
    if request.negative_prompt:
        arguments.extend(["--negative-prompt", request.negative_prompt])

    output_path = run_cli(
        settings.image_dir,
        arguments,
        settings.process_timeout_seconds,
    )
    return build_output("image", request.provider, output_path, settings)
