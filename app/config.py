"""Environment-based settings for the local studio."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


def _optional_path(name: str) -> Path | None:
    value = os.getenv(name, "").strip()
    return Path(value).expanduser().resolve() if value else None


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = "AI Media Toolkit"
    host: str = os.getenv("MEDIA_API_HOST", "127.0.0.1")
    port: int = int(os.getenv("MEDIA_API_PORT", "8000"))
    log_level: str = os.getenv("MEDIA_API_LOG_LEVEL", "INFO")
    output_dir: Path = Path(os.getenv("MEDIA_API_OUTPUT_DIR", str(ROOT_DIR / "outputs"))).expanduser().resolve()
    data_dir: Path = Path(os.getenv("MEDIA_API_DATA_DIR", str(ROOT_DIR / "data"))).expanduser().resolve()
    models_file: Path = Path(os.getenv("MEDIA_MODELS_FILE", str(ROOT_DIR / "models.json"))).expanduser().resolve()
    presets_file: Path = ROOT_DIR / "presets.json"
    audio_presets_file: Path = Path(os.getenv("MEDIA_AUDIO_PRESETS_FILE", str(ROOT_DIR / "audio-presets.json"))).expanduser().resolve()
    database_path: Path = Path(os.getenv("MEDIA_JOBS_DATABASE", str(ROOT_DIR / "data" / "jobs.db"))).expanduser().resolve()
    benchmarks_path: Path = Path(os.getenv("MEDIA_BENCHMARKS_FILE", str(ROOT_DIR / "data" / "benchmarks.jsonl"))).expanduser().resolve()
    voice_consents_path: Path = Path(os.getenv("MEDIA_VOICE_CONSENTS_FILE", str(ROOT_DIR / "data" / "voice-consents.json"))).expanduser().resolve()
    project_runs_dir: Path = Path(os.getenv("MEDIA_PROJECT_RUNS_DIR", str(ROOT_DIR / "data" / "projects"))).expanduser().resolve()
    model_cache_dir: Path | None = _optional_path("MEDIA_MODEL_CACHE_DIR")
    min_disk_free_gb: float = float(os.getenv("MEDIA_MIN_DISK_FREE_GB", "10"))
    audio_model: str = os.getenv("MEDIA_AUDIO_MODEL", "suno/bark-small")
    audio_device: str = os.getenv("MEDIA_AUDIO_DEVICE", "auto")
    transcription_model: str = os.getenv("MEDIA_TRANSCRIPTION_MODEL", "small")
    transcription_device: str = os.getenv("MEDIA_TRANSCRIPTION_DEVICE", "auto")
    transcription_compute_type: str = os.getenv("MEDIA_TRANSCRIPTION_COMPUTE_TYPE", "default")


settings = Settings()
