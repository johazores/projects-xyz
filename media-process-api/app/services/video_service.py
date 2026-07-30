"""Video API integration."""

from __future__ import annotations

from app.config import Settings
from app.models import GenerateRequest, MediaOutput, VideoFramesRequest, VideoResizeRequest
from app.services.common import build_output, output_directory
from app.services.runner import run_cli


def generate_video(request: GenerateRequest, settings: Settings) -> MediaOutput:
    output_path = run_cli(
        settings.video_dir,
        [
            "generate",
            "--prompt",
            request.prompt,
            "--provider",
            request.provider,
            "--output-dir",
            str(output_directory(settings, "video", request.project)),
        ],
        settings.process_timeout_seconds,
    )
    return build_output(
        "video", output_path, settings, operation="generate", provider=request.provider
    )


def resize_video(request: VideoResizeRequest, settings: Settings) -> MediaOutput:
    output_path = run_cli(
        settings.video_dir,
        [
            "resize",
            request.input_path,
            "--preset",
            request.preset,
            "--output-dir",
            str(output_directory(settings, "video", request.project)),
        ],
        settings.process_timeout_seconds,
    )
    return build_output("video", output_path, settings, operation="resize")


def extract_frames(request: VideoFramesRequest, settings: Settings) -> MediaOutput:
    output_path = run_cli(
        settings.video_dir,
        [
            "frames",
            request.input_path,
            "--fps",
            str(request.fps),
            "--output-dir",
            str(output_directory(settings, "video", request.project)),
        ],
        settings.process_timeout_seconds,
    )
    return build_output("video", output_path, settings, operation="frames")
