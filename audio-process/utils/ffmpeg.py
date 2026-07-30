"""FFmpeg-based audio processing."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess


def ensure_ffmpeg() -> str:
    """Return the FFmpeg executable path or raise a clear error."""

    executable = shutil.which("ffmpeg")
    if not executable:
        raise RuntimeError("FFmpeg is required. Install it and confirm `ffmpeg -version` works.")
    return executable


def run_ffmpeg(arguments: list[str]) -> None:
    """Run FFmpeg and convert failures into readable errors."""

    command = [ensure_ffmpeg(), "-y", *arguments]
    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        detail = result.stderr.strip().splitlines()
        message = detail[-1] if detail else "FFmpeg failed to process the audio file."
        raise RuntimeError(message)


def convert_to_mp3(input_path: Path, output_path: Path) -> Path:
    run_ffmpeg(["-i", str(input_path), "-codec:a", "libmp3lame", "-b:a", "192k", str(output_path)])
    return output_path


def normalize_audio(input_path: Path, output_path: Path) -> Path:
    run_ffmpeg(
        [
            "-i",
            str(input_path),
            "-af",
            "loudnorm",
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(output_path),
        ]
    )
    return output_path


def enhance_audio(input_path: Path, output_path: Path) -> Path:
    """Reduce steady noise, limit voice frequencies, and normalize loudness."""

    run_ffmpeg(
        [
            "-i",
            str(input_path),
            "-af",
            "highpass=f=80,lowpass=f=12000,afftdn=nf=-25,loudnorm",
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(output_path),
        ]
    )
    return output_path


def trim_audio(input_path: Path, output_path: Path, start: float, duration: float) -> Path:
    if start < 0:
        raise ValueError("start must be 0 or greater.")
    if duration <= 0:
        raise ValueError("duration must be greater than 0.")

    run_ffmpeg(
        [
            "-ss",
            str(start),
            "-i",
            str(input_path),
            "-t",
            str(duration),
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(output_path),
        ]
    )
    return output_path
