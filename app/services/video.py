"""Deterministic video resizing and frame extraction."""

from __future__ import annotations

from datetime import datetime, timezone
import json

from app.models import MediaOutput, VideoFramesRequest, VideoResizeRequest
from app.utils import ffmpeg
from app.utils.files import existing_file, media_output_dir, output_response, unique_directory, unique_path

VIDEO_PRESETS = {
    "youtube": (1920, 1080),
    "shorts": (1080, 1920),
    "square": (1080, 1080),
    "720p": (1280, 720),
}


def resize(request: VideoResizeRequest) -> MediaOutput:
    source = existing_file(request.input_path)
    width, height = VIDEO_PRESETS[request.preset]
    destination = unique_path(
        media_output_dir("video", request.project),
        f"{source.stem}-{request.preset}",
        ".mp4",
    )
    ffmpeg.resize_video(source, destination, width, height)
    return output_response("video", "resize", destination)


def frames(request: VideoFramesRequest) -> MediaOutput:
    source = existing_file(request.input_path)
    root = media_output_dir("video", request.project)
    frames_dir = unique_directory(root, f"{source.stem}-frames")
    ffmpeg.extract_frames(source, frames_dir / "frame-%06d.png", request.fps)
    frame_names = sorted(path.name for path in frames_dir.glob("frame-*.png"))
    manifest = unique_path(root, f"{source.stem}-frames", ".json")
    manifest.write_text(
        json.dumps(
            {
                "source": str(source),
                "fps": request.fps,
                "frame_count": len(frame_names),
                "frames_directory": str(frames_dir),
                "frames": frame_names,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return output_response("video", "frames", manifest)
