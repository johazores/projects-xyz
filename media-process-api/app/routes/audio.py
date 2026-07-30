"""Audio endpoints."""

from fastapi import APIRouter

from app.config import settings
from app.models import (
    AudioTranscribeRequest,
    AudioTrimRequest,
    GenerateRequest,
    LocalFileRequest,
    MediaOutput,
)
from app.services.audio_service import (
    convert_audio,
    enhance_audio,
    generate_audio,
    normalize_audio,
    transcribe_audio,
    trim_audio,
)

router = APIRouter(prefix="/audio", tags=["audio"])


@router.post("/generate", response_model=MediaOutput)
def generate(request: GenerateRequest) -> MediaOutput:
    return generate_audio(request, settings)


@router.post("/convert", response_model=MediaOutput)
def convert(request: LocalFileRequest) -> MediaOutput:
    return convert_audio(request, settings)


@router.post("/normalize", response_model=MediaOutput)
def normalize(request: LocalFileRequest) -> MediaOutput:
    return normalize_audio(request, settings)


@router.post("/enhance", response_model=MediaOutput)
def enhance(request: LocalFileRequest) -> MediaOutput:
    return enhance_audio(request, settings)


@router.post("/trim", response_model=MediaOutput)
def trim(request: AudioTrimRequest) -> MediaOutput:
    return trim_audio(request, settings)


@router.post("/transcribe", response_model=MediaOutput)
def transcribe(request: AudioTranscribeRequest) -> MediaOutput:
    return transcribe_audio(request, settings)
