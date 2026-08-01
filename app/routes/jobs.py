from fastapi import APIRouter, Query

from app.models import JobCreate, JobView
from app.runtime.state import registry, store, worker
from app.utils.files import MediaError
from app.workflows.youtube import validate_workflow

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobView, status_code=202)
def create_job(request: JobCreate) -> JobView:
    if request.kind == "model":
        spec = registry.get(request.target)
        if not spec.implemented:
            raise MediaError(f"Model {request.target} is planned but not implemented yet.")
    else:
        validate_workflow(request.target)
    return worker.submit(request.kind, request.target, request.payload)


@router.get("", response_model=list[JobView])
def list_jobs(limit: int = Query(default=50, ge=1, le=200)) -> list[JobView]:
    return store.list(limit)


@router.get("/{job_id}", response_model=JobView)
def get_job(job_id: str) -> JobView:
    return store.get(job_id)


@router.delete("/{job_id}", response_model=JobView)
def cancel_job(job_id: str) -> JobView:
    return worker.cancel(job_id)
