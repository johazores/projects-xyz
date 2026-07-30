"""FFmpeg-based video utilities."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess


def ensure_ffmpeg() -> str:
    executable = shutil.which("ffmpeg")
    if not executable:
        raise RuntimeError("FFmpeg is required. Install it and confirm `ffmpeg -version` works.")
    return executable


def run_ffmpeg(arguments: list[str]) -> None:
    command = [ensure_ffmpeg(), "-y", *arguments]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        lines = result.stderr.strip().splitlines()
        raise RuntimeError(lines[-1] if lines else "FFmpeg failed to process the video file.")


def resize_video(input_path: Path, output_path: Path, width: int, height: int) -> Path:
    """Resize and pad a video without stretching it."""

    filter_value = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
    )
    run_ffmpeg(
        [
            "-i",
            str(input_path),
            "-vf",
            filter_value,
            "-c:v",
            "libx264",
            "-crf",
            "20",
            "-preset",
            "veryfast",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(output_path),
        ]
    )
    return output_path


def extract_frames(input_path: Path, output_pattern: Path, fps: float) -> None:
    if fps <= 0:
        raise ValueError("fps must be greater than 0.")
    run_ffmpeg(["-i", str(input_path), "-vf", f"fps={fps}", str(output_pattern)])
