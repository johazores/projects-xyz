"""Video generation and practical video processing orchestration."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
from pathlib import Path

from config import VideoConfig
from providers import get_provider
from utils.ffmpeg import extract_frames, resize_video
from utils.files import create_output_path, ensure_directory
from utils.retry import run_with_retry

logger = logging.getLogger(__name__)

VIDEO_PRESETS = {
    "youtube": (1920, 1080),
    "shorts": (1080, 1920),
    "square": (1080, 1080),
    "720p": (1280, 720),
}


def generate_video(
    prompt: str,
    config: VideoConfig,
    provider_name: str | None = None,
    output_dir: str | Path | None = None,
) -> Path:
    """Generate a video artifact using the selected provider."""

    selected_name = provider_name or config.provider
    provider = get_provider(selected_name)
    destination = create_output_path(
        output_dir or config.output_dir,
        prompt,
        provider.file_extension,
        prefix="generated",
    )

    logger.info("Submitting video generation with the %s provider...", selected_name)
    path = run_with_retry(
        lambda: provider.generate(prompt, destination, config),
        retries=config.max_retries,
        delay_seconds=config.retry_delay_seconds,
    )
    logger.info("Video generation artifact saved to %s", path)
    return path


def resize_video_file(
    input_path: str | Path,
    config: VideoConfig,
    preset_name: str,
    output_dir: str | Path | None = None,
) -> Path:
    """Resize a local video to a common content format."""

    source = _existing_file(input_path)
    normalized = preset_name.lower()
    if normalized not in VIDEO_PRESETS:
        available = ", ".join(VIDEO_PRESETS)
        raise ValueError(f"Unknown video preset: {preset_name}. Available presets: {available}.")

    width, height = VIDEO_PRESETS[normalized]
    destination = (
        ensure_directory(output_dir or config.output_dir)
        / f"{source.stem}-{normalized}.mp4"
    )
    logger.info("Resizing %s to %sx%s...", source, width, height)
    return resize_video(source, destination, width, height)


def extract_video_frames(
    input_path: str | Path,
    config: VideoConfig,
    fps: float = 1.0,
    output_dir: str | Path | None = None,
) -> Path:
    """Extract PNG frames and return a small manifest describing the result."""

    source = _existing_file(input_path)
    base_dir = ensure_directory(output_dir or config.output_dir)
    frame_dir = ensure_directory(base_dir / f"{source.stem}-frames")
    pattern = frame_dir / "frame-%06d.png"
    logger.info("Extracting frames from %s at %s fps...", source, fps)
    extract_frames(source, pattern, fps)

    frame_files = sorted(path.name for path in frame_dir.glob("frame-*.png"))
    manifest_path = base_dir / f"{source.stem}-frames.json"
    manifest = {
        "source": str(source),
        "fps": fps,
        "frame_directory": str(frame_dir.resolve()),
        "frame_count": len(frame_files),
        "frames": frame_files,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def _existing_file(path: str | Path) -> Path:
    source = Path(path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Video file not found: {source}")
    return source
