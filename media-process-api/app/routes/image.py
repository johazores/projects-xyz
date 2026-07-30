"""Image endpoints."""

from fastapi import APIRouter

from app.config import settings
from app.models import (
    BatchOutput,
    ImageBackgroundRequest,
    ImageBatchRequest,
    ImageGenerateRequest,
    MediaOutput,
)
from app.services.image_service import (
    generate_image,
    generate_image_batch,
    get_presets,
    remove_background,
)

router = APIRouter(prefix="/image", tags=["image"])


@router.post("/generate", response_model=MediaOutput)
def generate(request: ImageGenerateRequest) -> MediaOutput:
    return generate_image(request, settings)


@router.post("/generate-batch", response_model=BatchOutput)
def generate_batch(request: ImageBatchRequest) -> BatchOutput:
    return generate_image_batch(request, settings)


@router.post("/remove-background", response_model=MediaOutput)
def remove_image_background(request: ImageBackgroundRequest) -> MediaOutput:
    return remove_background(request, settings)


@router.get("/presets")
def presets() -> dict[str, dict[str, str]]:
    return get_presets(settings)
