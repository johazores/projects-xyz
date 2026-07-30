"""Image endpoints."""

from fastapi import APIRouter

from app.config import settings
from app.models import ImageGenerateRequest, MediaOutput
from app.services.image_service import generate_image

router = APIRouter(prefix="/image", tags=["image"])


@router.post("/generate", response_model=MediaOutput)
def generate(request: ImageGenerateRequest) -> MediaOutput:
    """Generate an image artifact."""

    return generate_image(request, settings)
