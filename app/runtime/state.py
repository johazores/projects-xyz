"""Shared local runtime state."""

from app.config import settings
from app.core.registry import ModelRegistry
from app.runtime.job_store import JobStore
from app.runtime.model_manager import ModelManager
from app.runtime.worker import JobWorker

registry = ModelRegistry(settings.models_file)
store = JobStore(settings.database_path)
models = ModelManager(registry)
worker = JobWorker(store, models)
