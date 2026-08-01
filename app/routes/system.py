"""Local system diagnostics and benchmark history."""

from fastapi import APIRouter, Query

from app.runtime.hardware import hardware_snapshot
from app.runtime.state import benchmarks, models, worker

router = APIRouter(prefix="/system", tags=["system"])


@router.get("")
def system_status() -> dict[str, object]:
    return {
        "hardware": hardware_snapshot(),
        "active_model": models.active_id,
        "worker_running": worker.running,
        "queued_jobs": worker.queue.qsize(),
    }


@router.get("/gpu")
def gpu_status() -> dict[str, object]:
    return hardware_snapshot()


@router.get("/benchmarks")
def benchmark_history(limit: int = Query(default=50, ge=1, le=500)) -> list[dict[str, object]]:
    return benchmarks.list(limit)
