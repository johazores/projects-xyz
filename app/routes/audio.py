from fastapi import APIRouter

from app.models import (
    AudioTranscribeRequest,
    AudioTrimRequest,
    GenerateRequest,
    LocalFileRequest,
    MediaOutput,
)
from app.services import audio

router = APIRouter(prefix="/audio", tags=["audio"])

router.post("/generate", response_model=MediaOutput)(audio.generate)
router.post("/convert", response_model=MediaOutput)(audio.convert)
router.post("/normalize", response_model=MediaOutput)(audio.normalize)
router.post("/enhance", response_model=MediaOutput)(audio.enhance)
router.post("/trim", response_model=MediaOutput)(audio.trim)
router.post("/transcribe", response_model=MediaOutput)(audio.transcribe_file)
