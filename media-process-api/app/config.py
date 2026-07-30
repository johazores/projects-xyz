"""Small environment-based configuration for the local API."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parents[1]
REPOSITORY_DIR = PROJECT_DIR.parent

load_dotenv(PROJECT_DIR / ".env")


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings with local development defaults."""

    app_name: str = os.getenv("MEDIA_API_NAME", "AI Media Processing Toolkit API")
    host: str = os.getenv("MEDIA_API_HOST", "127.0.0.1")
    port: int = int(os.getenv("MEDIA_API_PORT", "8000"))
    log_level: str = os.getenv("MEDIA_API_LOG_LEVEL", "INFO")
    process_timeout_seconds: int = int(os.getenv("MEDIA_API_PROCESS_TIMEOUT", "3600"))
    output_dir: Path = Path(
        os.getenv("MEDIA_API_OUTPUT_DIR", str(PROJECT_DIR / "outputs"))
    ).resolve()

    audio_dir: Path = REPOSITORY_DIR / "audio-process"
    image_dir: Path = REPOSITORY_DIR / "image-process"
    video_dir: Path = REPOSITORY_DIR / "video-process"


settings = Settings()

PROVIDER_CATALOG = {
    "audio": {
        "demo": ["local-tone"],
        "bark": ["suno/bark-small"],
    },
    "image": {
        "demo": ["prompt-card-svg"],
    },
    "video": {
        "demo": ["request-manifest"],
    },
}

CAPABILITY_CATALOG = {
    "audio": ["generate", "convert", "normalize", "enhance", "transcribe", "trim"],
    "image": ["generate", "generate-batch", "remove-background", "presets"],
    "video": ["generate", "resize", "frames"],
}
