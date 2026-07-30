"""Audio generation and processing orchestration."""

from __future__ import annotations

import logging
from pathlib import Path

from config import AudioConfig
from providers import get_provider
from utils.ffmpeg import convert_to_mp3, normalize_audio, trim_audio
from utils.files import create_output_path, ensure_directory
from utils.retry import run_with_retry

logger = logging.getLogger(__name__)


def generate_audio(
    prompt: str,
    config: AudioConfig,
    provider_name: str | None = None,
    output_dir: str | Path | None = None,
) -> Path:
    """Generate audio using the selected provider."""

    provider = get_provider(provider_name or config.provider)
    destination = create_output_path(
        output_dir or config.output_dir,
        prompt,
        provider.file_extension,
        prefix="generated",
    )

    logger.info("Generating audio with the %s provider...", provider_name or config.provider)
    path = run_with_retry(
        lambda: provider.generate(prompt, destination, config),
        retries=config.max_retries,
        delay_seconds=config.retry_delay_seconds,
    )
    logger.info("Audio saved to %s", path)
    return path


def convert_audio_file(
    input_path: str | Path,
    config: AudioConfig,
    output_dir: str | Path | None = None,
) -> Path:
    """Convert an audio file to MP3."""

    source = _existing_file(input_path)
    destination = ensure_directory(output_dir or config.output_dir) / f"{source.stem}-converted.mp3"
    logger.info("Converting %s...", source)
    return convert_to_mp3(source, destination)


def normalize_audio_file(
    input_path: str | Path,
    config: AudioConfig,
    output_dir: str | Path | None = None,
) -> Path:
    """Normalize an audio file and save an MP3."""

    source = _existing_file(input_path)
    destination = ensure_directory(output_dir or config.output_dir) / f"{source.stem}-normalized.mp3"
    logger.info("Normalizing %s...", source)
    return normalize_audio(source, destination)


def trim_audio_file(
    input_path: str | Path,
    start: float,
    duration: float,
    config: AudioConfig,
    output_dir: str | Path | None = None,
) -> Path:
    """Trim an audio file and save an MP3."""

    source = _existing_file(input_path)
    destination = ensure_directory(output_dir or config.output_dir) / f"{source.stem}-trimmed.mp3"
    logger.info("Trimming %s...", source)
    return trim_audio(source, destination, start, duration)


def _existing_file(path: str | Path) -> Path:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Audio file not found: {source}")
    return source
