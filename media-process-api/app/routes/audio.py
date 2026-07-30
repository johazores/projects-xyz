"""Audio endpoints."""

from fastapi import APIRouter

from app.config import settings
from app.models import GenerateRequest, MediaOutput
from app.services.audio_service import generate_audio

router = APIRouter(prefix="/audio", tags=["audio"])


@router.post("/generate", response_model=MediaOutput)
def generate(request: GenerateRequest) -> MediaOutput:
    """Generate an audio artifact."""

    return generate_audio(request, settings)
