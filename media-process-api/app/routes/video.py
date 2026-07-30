"""Video endpoints."""

from fastapi import APIRouter

from app.config import settings
from app.models import GenerateRequest, MediaOutput
from app.services.video_service import generate_video

router = APIRouter(prefix="/video", tags=["video"])


@router.post("/generate", response_model=MediaOutput)
def generate(request: GenerateRequest) -> MediaOutput:
    """Generate a video artifact or request manifest."""

    return generate_video(request, settings)
