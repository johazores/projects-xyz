"""Shared local runtime state."""

from app.config import settings
from app.core.registry import ModelRegistry
from app.runtime.audio_presets import AudioPresetStore
from app.runtime.benchmark_store import BenchmarkStore
from app.runtime.job_store import JobStore
from app.runtime.model_manager import ModelManager
from app.runtime.project_store import ProjectStore
from app.runtime.voice_consent import VoiceConsentStore
from app.runtime.worker import JobWorker

registry = ModelRegistry(settings.models_file)
store = JobStore(settings.database_path)
benchmarks = BenchmarkStore(settings.benchmarks_path)
voice_consents = VoiceConsentStore(settings.voice_consents_path)
projects = ProjectStore(settings.project_runs_dir)
audio_presets = AudioPresetStore(settings.audio_presets_file)
models = ModelManager(registry, benchmarks)
worker = JobWorker(store, models, projects, audio_presets)
