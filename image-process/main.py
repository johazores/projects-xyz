"""Image generation orchestration."""

from __future__ import annotations

import logging
from pathlib import Path

from config import ImageConfig
from providers import get_provider
from utils.files import create_output_path
from utils.retry import run_with_retry

logger = logging.getLogger(__name__)


def generate_image(
    prompt: str,
    config: ImageConfig,
    negative_prompt: str | None = None,
    provider_name: str | None = None,
    output_dir: str | Path | None = None,
) -> Path:
    """Generate an image using the selected provider."""

    selected_name = provider_name or config.provider
    provider = get_provider(selected_name)
    destination = create_output_path(
        output_dir or config.output_dir,
        prompt,
        provider.file_extension,
        prefix="generated",
    )

    logger.info("Generating image with the %s provider...", selected_name)
    path = run_with_retry(
        lambda: provider.generate(prompt, negative_prompt, destination, config),
        retries=config.max_retries,
        delay_seconds=config.retry_delay_seconds,
    )
    logger.info("Image saved to %s", path)
    return path
