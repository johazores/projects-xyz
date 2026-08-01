"""Durable workflow project runs and resume controls."""

from fastapi import APIRouter, Query

from app.models import JobView
from app.runtime.state import projects, worker

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/runs")
def list_project_runs(project: str | None = None, limit: int = Query(default=100, ge=1, le=500)) -> list[dict]:
    return projects.list(project=project, limit=limit)


@router.get("/runs/{run_id}")
def get_project_run(run_id: str) -> dict:
    return projects.get(run_id)


@router.post("/runs/{run_id}/resume", response_model=JobView, status_code=202)
def resume_project_run(run_id: str) -> JobView:
    return worker.resume(run_id)
