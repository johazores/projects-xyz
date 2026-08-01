from typing import Any

from fastapi import APIRouter

from app.models import JobView, ThumbnailWorkflowRequest, WorkflowView
from app.runtime.state import worker
from app.workflows.youtube import list_workflows, validate_workflow

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("", response_model=list[WorkflowView])
def workflows() -> list[WorkflowView]:
    return list_workflows()


@router.post("/youtube.thumbnail", response_model=JobView, status_code=202)
def run_thumbnail(request: ThumbnailWorkflowRequest) -> JobView:
    validate_workflow("youtube.thumbnail")
    return worker.submit("workflow", "youtube.thumbnail", request.model_dump(exclude_none=True))


@router.post("/{workflow_id}", response_model=JobView, status_code=202)
def run_workflow(workflow_id: str, payload: dict[str, Any]) -> JobView:
    validate_workflow(workflow_id)
    return worker.submit("workflow", workflow_id, payload)
