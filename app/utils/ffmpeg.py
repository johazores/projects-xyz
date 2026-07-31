"""Focused FFmpeg operations used by audio and video routes."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

from app.utils.files import MediaError


def run_ffmpeg(arguments: list[str]) -> None:
    executable = shutil.which("ffmpeg")
    if not executable:
        raise MediaError("FFmpeg is required. Install it and confirm `ffmpeg -version` works.")

    result = subprocess.run(
        [executable, "-y", *arguments],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        lines = result.stderr.strip().splitlines()
        raise MediaError(lines[-1] if lines else "FFmpeg failed.")


def convert_audio(source: Path, destination: Path) -> None:
    run_ffmpeg(["-i", str(source), "-codec:a", "libmp3lame", "-b:a", "192k", str(destination)])


def normalize_audio(source: Path, destination: Path) -> None:
    run_ffmpeg(["-i", str(source), "-af", "loudnorm", "-codec:a", "libmp3lame", "-b:a", "192k", str(destination)])


def enhance_audio(source: Path, destination: Path) -> None:
    run_ffmpeg([
        "-i", str(source),
        "-af", "highpass=f=80,lowpass=f=12000,afftdn=nf=-25,loudnorm",
        "-codec:a", "libmp3lame", "-b:a", "192k", str(destination),
    ])


def trim_audio(source: Path, destination: Path, start: float, duration: float) -> None:
    run_ffmpeg([
        "-ss", str(start), "-i", str(source), "-t", str(duration),
        "-codec:a", "libmp3lame", "-b:a", "192k", str(destination),
    ])


def resize_video(source: Path, destination: Path, width: int, height: int) -> None:
    filter_value = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1"
    )
    run_ffmpeg([
        "-i", str(source), "-vf", filter_value,
        "-c:v", "libx264", "-crf", "20", "-preset", "medium",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        str(destination),
    ])


def extract_frames(source: Path, output_pattern: Path, fps: float) -> None:
    run_ffmpeg(["-i", str(source), "-vf", f"fps={fps}", str(output_pattern)])
