"""Image API integration."""

from __future__ import annotations

import json

from app.config import Settings
from app.models import (
    BatchOutput,
    ImageBackgroundRequest,
    ImageBatchRequest,
    ImageGenerateRequest,
    MediaOutput,
)
from app.services.common import build_output, output_directory
from app.services.runner import run_cli


def generate_image(request: ImageGenerateRequest, settings: Settings) -> MediaOutput:
    arguments = [
        "generate",
        "--prompt",
        request.prompt,
        "--provider",
        request.provider,
        "--output-dir",
        str(output_directory(settings, "image", request.project)),
    ]
    if request.negative_prompt:
        arguments.extend(["--negative-prompt", request.negative_prompt])
    if request.preset:
        arguments.extend(["--preset", request.preset])

    output_path = run_cli(settings.image_dir, arguments, settings.process_timeout_seconds)
    return build_output(
        "image", output_path, settings, operation="generate", provider=request.provider
    )


def generate_image_batch(request: ImageBatchRequest, settings: Settings) -> BatchOutput:
    prompts = [prompt.strip() for prompt in request.prompts if prompt.strip()]
    if not prompts:
        raise ValueError("At least one non-empty prompt is required.")

    items = [
        generate_image(
            ImageGenerateRequest(
                prompt=prompt,
                provider=request.provider,
                negative_prompt=request.negative_prompt,
                preset=request.preset,
                project=request.project,
            ),
            settings,
        )
        for prompt in prompts
    ]
    return BatchOutput(items=items)


def remove_background(request: ImageBackgroundRequest, settings: Settings) -> MediaOutput:
    output_path = run_cli(
        settings.image_dir,
        [
            "remove-background",
            request.input_path,
            "--model",
            request.model,
            "--output-dir",
            str(output_directory(settings, "image", request.project)),
        ],
        settings.process_timeout_seconds,
    )
    return build_output(
        "image", output_path, settings, operation="remove-background", provider="rembg"
    )


def get_presets(settings: Settings) -> dict[str, dict[str, str]]:
    preset_path = settings.image_dir / "presets.json"
    return json.loads(preset_path.read_text(encoding="utf-8"))
