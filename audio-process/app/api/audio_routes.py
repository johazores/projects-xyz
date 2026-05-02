from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from app.core.config import Settings, get_settings
from app.core.errors import AudioGenerationError, AudioProcessingError, FFmpegNotFoundError
from app.services.audio_generation_service import AudioGenerationService
from app.services.ffmpeg_service import FFmpegService
from app.utils.files import (
    ensure_directory,
    remove_file_if_exists,
    safe_file_extension,
    save_upload_file,
    unique_filename,
)

router = APIRouter(prefix="/audio", tags=["Audio"])


class AudioResponse(BaseModel):
    message: str
    filename: str
    url: str


class GenerateAudioRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)


def build_file_url(settings: Settings, filename: str) -> str:
    return f"{settings.base_url.rstrip('/')}/processed/{filename}"


def save_uploaded_audio(audio: UploadFile, settings: Settings) -> Path:
    upload_dir = ensure_directory(settings.upload_dir)
    extension = safe_file_extension(audio.filename, fallback=".audio")
    input_filename = unique_filename("upload", extension)
    input_path = upload_dir / input_filename
    save_upload_file(audio, input_path)
    return input_path


@router.post("/convert-to-mp3", response_model=AudioResponse)
async def convert_to_mp3(
    audio: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
):
    input_path = save_uploaded_audio(audio, settings)
    output_filename = unique_filename("converted", ".mp3")
    output_path = ensure_directory(settings.processed_dir) / output_filename

    try:
        FFmpegService().convert_to_mp3(input_path, output_path)
    except (FFmpegNotFoundError, AudioProcessingError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        remove_file_if_exists(input_path)

    return AudioResponse(
        message="Audio converted to MP3 successfully.",
        filename=output_filename,
        url=build_file_url(settings, output_filename),
    )


@router.post("/normalize", response_model=AudioResponse)
async def normalize_audio(
    audio: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
):
    input_path = save_uploaded_audio(audio, settings)
    output_filename = unique_filename("normalized", ".mp3")
    output_path = ensure_directory(settings.processed_dir) / output_filename

    try:
        FFmpegService().normalize_audio(input_path, output_path)
    except (FFmpegNotFoundError, AudioProcessingError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        remove_file_if_exists(input_path)

    return AudioResponse(
        message="Audio normalized successfully.",
        filename=output_filename,
        url=build_file_url(settings, output_filename),
    )


@router.post("/trim", response_model=AudioResponse)
async def trim_audio(
    audio: UploadFile = File(...),
    start: float = Form(0),
    duration: float = Form(10),
    settings: Settings = Depends(get_settings),
):
    if start < 0:
        raise HTTPException(status_code=400, detail="start must be 0 or greater.")

    if duration <= 0:
        raise HTTPException(status_code=400, detail="duration must be greater than 0.")

    input_path = save_uploaded_audio(audio, settings)
    output_filename = unique_filename("trimmed", ".mp3")
    output_path = ensure_directory(settings.processed_dir) / output_filename

    try:
        FFmpegService().trim_audio(input_path, output_path, start, duration)
    except (FFmpegNotFoundError, AudioProcessingError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        remove_file_if_exists(input_path)

    return AudioResponse(
        message="Audio trimmed successfully.",
        filename=output_filename,
        url=build_file_url(settings, output_filename),
    )


@router.post("/generate", response_model=AudioResponse)
async def generate_audio(
    request: GenerateAudioRequest,
    settings: Settings = Depends(get_settings),
):
    output_filename = unique_filename("generated", ".wav")
    output_path = ensure_directory(settings.processed_dir) / output_filename

    try:
        AudioGenerationService(settings).generate_from_text(request.text, output_path)
    except AudioGenerationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return AudioResponse(
        message="Audio generated successfully.",
        filename=output_filename,
        url=build_file_url(settings, output_filename),
    )
