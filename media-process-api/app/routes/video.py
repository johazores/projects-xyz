"""Video endpoints."""

from fastapi import APIRouter

from app.config import settings
from app.models import GenerateRequest, MediaOutput, VideoFramesRequest, VideoResizeRequest
from app.services.video_service import extract_frames, generate_video, resize_video

router = APIRouter(prefix="/video", tags=["video"])


@router.post("/generate", response_model=MediaOutput)
def generate(request: GenerateRequest) -> MediaOutput:
    return generate_video(request, settings)


@router.post("/resize", response_model=MediaOutput)
def resize(request: VideoResizeRequest) -> MediaOutput:
    return resize_video(request, settings)


@router.post("/frames", response_model=MediaOutput)
def frames(request: VideoFramesRequest) -> MediaOutput:
    return extract_frames(request, settings)
