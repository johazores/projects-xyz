"""Image generation and practical image processing orchestration."""

from __future__ import annotations

import logging
from pathlib import Path

from config import ImageConfig
from providers import get_provider
from utils.background import remove_background
from utils.files import create_output_path, ensure_directory
from utils.presets import apply_preset
from utils.retry import run_with_retry

logger = logging.getLogger(__name__)


def generate_image(
    prompt: str,
    config: ImageConfig,
    negative_prompt: str | None = None,
    provider_name: str | None = None,
    output_dir: str | Path | None = None,
    preset_name: str | None = None,
) -> Path:
    """Generate an image using the selected provider."""

    prepared_prompt, prepared_negative = apply_preset(prompt, negative_prompt, preset_name)
    selected_name = provider_name or config.provider
    provider = get_provider(selected_name)
    destination = create_output_path(
        output_dir or config.output_dir,
        prepared_prompt,
        provider.file_extension,
        prefix="generated",
    )

    logger.info("Generating image with the %s provider...", selected_name)
    path = run_with_retry(
        lambda: provider.generate(prepared_prompt, prepared_negative, destination, config),
        retries=config.max_retries,
        delay_seconds=config.retry_delay_seconds,
    )
    logger.info("Image saved to %s", path)
    return path


def generate_image_batch(
    prompts: list[str],
    config: ImageConfig,
    negative_prompt: str | None = None,
    provider_name: str | None = None,
    output_dir: str | Path | None = None,
    preset_name: str | None = None,
) -> list[Path]:
    """Generate images sequentially from a small prompt list."""

    clean_prompts = [prompt.strip() for prompt in prompts if prompt.strip()]
    if not clean_prompts:
        raise ValueError("At least one non-empty prompt is required.")

    outputs = []
    for index, prompt in enumerate(clean_prompts, start=1):
        logger.info("Generating image %s of %s...", index, len(clean_prompts))
        outputs.append(
            generate_image(
                prompt=prompt,
                config=config,
                negative_prompt=negative_prompt,
                provider_name=provider_name,
                output_dir=output_dir,
                preset_name=preset_name,
            )
        )
    return outputs


def remove_image_background(
    input_path: str | Path,
    config: ImageConfig,
    model_name: str = "u2net",
    output_dir: str | Path | None = None,
) -> Path:
    """Remove a local image background with the optional rembg package."""

    source = Path(input_path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Image file not found: {source}")

    destination = ensure_directory(output_dir or config.output_dir) / f"{source.stem}-no-bg.png"
    logger.info("Removing the background from %s with %s...", source, model_name)
    return remove_background(source, destination, model_name)
