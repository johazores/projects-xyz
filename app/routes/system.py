"""Local system diagnostics, readiness, cleanup, and benchmark history."""

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.config import settings
from app.runtime.cleanup import cleanup
from app.runtime.hardware import hardware_snapshot
from app.runtime.readiness import readiness_snapshot, storage_snapshot
from app.runtime.state import benchmarks, models, projects, registry, worker

router = APIRouter(prefix="/system", tags=["system"])


class CleanupRequest(BaseModel):
    project: str | None = Field(default=None, max_length=80)
    older_than_days: int | None = Field(default=None, ge=0, le=3650)
    include_project_runs: bool = False
    include_model_cache: bool = False
    dry_run: bool = True
    confirm: bool = False


@router.get("")
def system_status() -> dict[str, object]:
    return {"hardware": hardware_snapshot(), "active_model": models.active_id, "worker_running": worker.running, "queued_jobs": worker.queue.qsize(), "active_projects": sorted(projects.active_projects())}


@router.get("/gpu")
def gpu_status() -> dict[str, object]:
    return hardware_snapshot()


@router.get("/benchmarks")
def benchmark_history(limit: int = Query(default=50, ge=1, le=500)) -> list[dict[str, object]]:
    return benchmarks.list(limit)


@router.get("/readiness")
def readiness() -> dict[str, object]:
    return readiness_snapshot(settings, registry)


@router.get("/storage")
def storage() -> dict[str, object]:
    return storage_snapshot(settings)


@router.post("/cleanup")
def cleanup_files(request: CleanupRequest) -> dict[str, object]:
    return cleanup(settings=settings, projects=projects, project=request.project, older_than_days=request.older_than_days, include_project_runs=request.include_project_runs, include_model_cache=request.include_model_cache, dry_run=request.dry_run, confirm=request.confirm)
