"""Audio API integration."""

from __future__ import annotations

from app.config import Settings
from app.models import (
    AudioTranscribeRequest,
    AudioTrimRequest,
    GenerateRequest,
    LocalFileRequest,
    MediaOutput,
)
from app.services.common import build_output, output_directory
from app.services.runner import run_cli


def generate_audio(request: GenerateRequest, settings: Settings) -> MediaOutput:
    output_path = run_cli(
        settings.audio_dir,
        [
            "generate",
            "--prompt",
            request.prompt,
            "--provider",
            request.provider,
            "--output-dir",
            str(output_directory(settings, "audio", request.project)),
        ],
        settings.process_timeout_seconds,
    )
    return build_output(
        "audio", output_path, settings, operation="generate", provider=request.provider
    )


def convert_audio(request: LocalFileRequest, settings: Settings) -> MediaOutput:
    output_path = run_cli(
        settings.audio_dir,
        [
            "convert",
            request.input_path,
            "--output-dir",
            str(output_directory(settings, "audio", request.project)),
        ],
        settings.process_timeout_seconds,
    )
    return build_output("audio", output_path, settings, operation="convert")


def normalize_audio(request: LocalFileRequest, settings: Settings) -> MediaOutput:
    output_path = run_cli(
        settings.audio_dir,
        [
            "normalize",
            request.input_path,
            "--output-dir",
            str(output_directory(settings, "audio", request.project)),
        ],
        settings.process_timeout_seconds,
    )
    return build_output("audio", output_path, settings, operation="normalize")


def enhance_audio(request: LocalFileRequest, settings: Settings) -> MediaOutput:
    output_path = run_cli(
        settings.audio_dir,
        [
            "enhance",
            request.input_path,
            "--output-dir",
            str(output_directory(settings, "audio", request.project)),
        ],
        settings.process_timeout_seconds,
    )
    return build_output("audio", output_path, settings, operation="enhance")


def trim_audio(request: AudioTrimRequest, settings: Settings) -> MediaOutput:
    output_path = run_cli(
        settings.audio_dir,
        [
            "trim",
            request.input_path,
            "--start",
            str(request.start),
            "--duration",
            str(request.duration),
            "--output-dir",
            str(output_directory(settings, "audio", request.project)),
        ],
        settings.process_timeout_seconds,
    )
    return build_output("audio", output_path, settings, operation="trim")


def transcribe_audio(request: AudioTranscribeRequest, settings: Settings) -> MediaOutput:
    arguments = [
        "transcribe",
        request.input_path,
        "--format",
        request.output_format,
        "--output-dir",
        str(output_directory(settings, "audio", request.project)),
    ]
    for name, value in (
        ("--language", request.language),
        ("--model", request.model),
        ("--device", request.device),
        ("--compute-type", request.compute_type),
    ):
        if value:
            arguments.extend([name, value])

    output_path = run_cli(
        settings.audio_dir,
        arguments,
        settings.process_timeout_seconds,
    )
    return build_output("audio", output_path, settings, operation="transcribe")
