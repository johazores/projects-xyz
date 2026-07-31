"""Audio generation, cleanup, and transcription."""

from __future__ import annotations

import math
from pathlib import Path
import wave

from app.config import settings
from app.models import (
    AudioTranscribeRequest,
    AudioTrimRequest,
    GenerateRequest,
    LocalFileRequest,
    MediaOutput,
)
from app.utils import ffmpeg
from app.utils.files import (
    MediaError,
    existing_file,
    media_output_dir,
    output_response,
    unique_path,
)
from app.utils.transcription import transcribe


def generate(request: GenerateRequest) -> MediaOutput:
    provider = request.provider.strip().lower()
    destination = unique_path(
        media_output_dir("audio", request.project), request.prompt, ".wav"
    )

    if provider == "demo":
        _generate_tone(destination)
    elif provider == "bark":
        _generate_bark(request.prompt, destination)
    else:
        raise MediaError("Unknown audio provider. Available providers: demo, bark.")

    return output_response("audio", "generate", destination, provider)


def convert(request: LocalFileRequest) -> MediaOutput:
    source = existing_file(request.input_path)
    destination = unique_path(media_output_dir("audio", request.project), f"{source.stem}-converted", ".mp3")
    ffmpeg.convert_audio(source, destination)
    return output_response("audio", "convert", destination)


def normalize(request: LocalFileRequest) -> MediaOutput:
    source = existing_file(request.input_path)
    destination = unique_path(media_output_dir("audio", request.project), f"{source.stem}-normalized", ".mp3")
    ffmpeg.normalize_audio(source, destination)
    return output_response("audio", "normalize", destination)


def enhance(request: LocalFileRequest) -> MediaOutput:
    source = existing_file(request.input_path)
    destination = unique_path(media_output_dir("audio", request.project), f"{source.stem}-enhanced", ".mp3")
    ffmpeg.enhance_audio(source, destination)
    return output_response("audio", "enhance", destination)


def trim(request: AudioTrimRequest) -> MediaOutput:
    source = existing_file(request.input_path)
    destination = unique_path(media_output_dir("audio", request.project), f"{source.stem}-trimmed", ".mp3")
    ffmpeg.trim_audio(source, destination, request.start, request.duration)
    return output_response("audio", "trim", destination)


def transcribe_file(request: AudioTranscribeRequest) -> MediaOutput:
    source = existing_file(request.input_path)
    destination = unique_path(
        media_output_dir("audio", request.project),
        f"{source.stem}-transcript",
        f".{request.output_format}",
    )
    transcribe(
        source,
        destination,
        model_name=request.model or settings.transcription_model,
        device=request.device or settings.transcription_device,
        compute_type=request.compute_type or settings.transcription_compute_type,
        language=request.language,
        output_format=request.output_format,
    )
    return output_response("audio", "transcribe", destination)


def _generate_tone(destination: Path) -> None:
    sample_rate = 24_000
    duration = 2.0
    frequency = 440.0
    with wave.open(str(destination), "w") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        for index in range(int(sample_rate * duration)):
            envelope = min(
                1.0,
                index / (sample_rate * 0.05),
                (sample_rate * duration - index) / (sample_rate * 0.05),
            )
            value = int(
                12_000
                * envelope
                * math.sin(2 * math.pi * frequency * index / sample_rate)
            )
            output.writeframesraw(value.to_bytes(2, "little", signed=True))


def _generate_bark(prompt: str, destination: Path) -> None:
    try:
        import numpy as np
        import scipy.io.wavfile
        import torch
        from transformers import pipeline
    except ImportError as exc:
        raise MediaError(
            "Bark is optional. Install `requirements-bark.txt` and a compatible torch build."
        ) from exc

    device = settings.audio_device
    if device == "cuda" and not torch.cuda.is_available():
        raise MediaError("CUDA was requested, but PyTorch cannot detect a CUDA device.")
    pipeline_device = -1 if device == "cpu" else (0 if torch.cuda.is_available() else -1)
    generator = pipeline("text-to-audio", model=settings.audio_model, device=pipeline_device)
    result = generator(prompt)
    audio = np.asarray(result["audio"]).squeeze()
    scipy.io.wavfile.write(str(destination), result["sampling_rate"], audio)
