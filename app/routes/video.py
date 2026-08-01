from fastapi import APIRouter

from app.models import JobView, MediaOutput, VideoFramesRequest, VideoGenerateRequest, VideoResizeRequest
from app.runtime.state import registry, worker
from app.services import video
from app.utils.files import MediaError

router = APIRouter(prefix="/video", tags=["video"])


@router.post("/generate", response_model=JobView, status_code=202)
def generate(request: VideoGenerateRequest) -> JobView:
    spec = registry.get(request.model)
    if not spec.implemented:
        raise MediaError(f"Model {request.model} is planned but not implemented yet.")
    return worker.submit(
        "model",
        request.model,
        request.model_dump(exclude={"model"}, exclude_none=True),
    )


router.post("/resize", response_model=MediaOutput)(video.resize)
router.post("/frames", response_model=MediaOutput)(video.frames)
