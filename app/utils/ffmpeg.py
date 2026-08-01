"""Focused FFmpeg operations used by local media workflows."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import tempfile

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


def probe_duration(source: Path) -> float:
    executable = shutil.which("ffprobe")
    if not executable:
        raise MediaError("ffprobe is required and is normally installed with FFmpeg.")
    result = subprocess.run(
        [
            executable,
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(source),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        duration = float(result.stdout.strip())
    except ValueError as exc:
        raise MediaError("Unable to determine media duration.") from exc
    if result.returncode != 0 or duration <= 0:
        raise MediaError("Unable to determine media duration.")
    return duration


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
    run_ffmpeg([
        "-i", str(source),
        "-vf", _fit_filter(width, height),
        "-c:v", "libx264", "-crf", "20", "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
        str(destination),
    ])


def extract_frames(source: Path, output_pattern: Path, fps: float) -> None:
    run_ffmpeg(["-i", str(source), "-vf", f"fps={fps}", str(output_pattern)])


def create_image_clip(
    source: Path,
    destination: Path,
    *,
    duration: float,
    width: int,
    height: int,
    fps: int,
) -> None:
    run_ffmpeg([
        "-loop", "1",
        "-i", str(source),
        "-t", f"{duration:.3f}",
        "-vf", f"{_fit_filter(width, height)},fps={fps}",
        "-an",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(destination),
    ])


def normalize_video_clip(
    source: Path,
    destination: Path,
    *,
    duration: float,
    width: int,
    height: int,
    fps: int,
) -> None:
    run_ffmpeg([
        "-stream_loop", "-1",
        "-i", str(source),
        "-t", f"{duration:.3f}",
        "-vf", f"{_fit_filter(width, height)},fps={fps}",
        "-an",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(destination),
    ])


def concatenate_videos(sources: list[Path], destination: Path) -> None:
    if not sources:
        raise MediaError("At least one video clip is required.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", encoding="utf-8", delete=False,
        dir=destination.parent,
    ) as handle:
        list_path = Path(handle.name)
        for source in sources:
            escaped = str(source.resolve()).replace("'", "'\\''")
            handle.write(f"file '{escaped}'\n")
    try:
        run_ffmpeg([
            "-f", "concat", "-safe", "0", "-i", str(list_path),
            "-c", "copy", "-movflags", "+faststart", str(destination),
        ])
    finally:
        list_path.unlink(missing_ok=True)


def mux_audio(video: Path, audio: Path, destination: Path) -> None:
    run_ffmpeg([
        "-i", str(video),
        "-i", str(audio),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(destination),
    ])


def burn_subtitles(source: Path, subtitles: Path, destination: Path) -> None:
    subtitle_value = str(subtitles.resolve()).replace("\\", "/")
    subtitle_value = subtitle_value.replace(":", "\\:").replace("'", "\\'")
    run_ffmpeg([
        "-i", str(source),
        "-vf", f"subtitles='{subtitle_value}'",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "copy", "-movflags", "+faststart", str(destination),
    ])


def _fit_filter(width: int, height: int) -> str:
    return (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1"
    )


def concatenate_audio(
    sources: list[Path],
    destination: Path,
    *,
    pauses: list[float] | None = None,
) -> None:
    if not sources:
        raise MediaError("At least one audio source is required.")
    pauses = pauses or [0.0] * len(sources)
    if len(pauses) != len(sources):
        raise MediaError("Audio pause values must match the number of sources.")
    arguments: list[str] = []
    for source in sources:
        arguments.extend(["-i", str(source)])
    filters: list[str] = []
    labels: list[str] = []
    for index, pause in enumerate(pauses):
        duration = probe_duration(sources[index]) + max(0.0, pause)
        label = f"a{index}"
        filters.append(
            f"[{index}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,"
            f"apad=pad_dur={max(0.0, pause):.3f},atrim=0:{duration:.3f}[{label}]"
        )
        labels.append(f"[{label}]")
    filters.append(f"{''.join(labels)}concat=n={len(sources)}:v=0:a=1[outa]")
    run_ffmpeg([
        *arguments,
        "-filter_complex", ";".join(filters),
        "-map", "[outa]",
        "-codec:a", "libmp3lame", "-b:a", "192k",
        str(destination),
    ])


def mix_background_music(
    narration: Path,
    music: Path,
    destination: Path,
    *,
    music_volume: float = 0.12,
    fade_seconds: float = 2.0,
) -> None:
    duration = probe_duration(narration)
    fade_start = max(0.0, duration - max(0.0, fade_seconds))
    run_ffmpeg([
        "-i", str(narration),
        "-stream_loop", "-1", "-i", str(music),
        "-filter_complex",
        (
            f"[0:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[voice];"
            f"[1:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,"
            f"volume={max(0.0, min(1.0, music_volume)):.3f},atrim=0:{duration:.3f},"
            f"afade=t=out:st={fade_start:.3f}:d={max(0.1, fade_seconds):.3f}[music];"
            "[voice][music]amix=inputs=2:duration=first:dropout_transition=2,loudnorm[outa]"
        ),
        "-map", "[outa]",
        "-codec:a", "libmp3lame", "-b:a", "192k",
        str(destination),
    ])


def overlay_audio_cues(
    base_audio: Path,
    cues: list[tuple[Path, float, float]],
    destination: Path,
) -> None:
    if not cues:
        shutil.copy2(base_audio, destination)
        return
    arguments = ["-i", str(base_audio)]
    for source, _, _ in cues:
        arguments.extend(["-i", str(source)])
    filters = ["[0:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[base]"]
    labels = ["[base]"]
    for index, (_, start_seconds, volume) in enumerate(cues, start=1):
        delay = max(0, round(start_seconds * 1000))
        label = f"cue{index}"
        filters.append(
            f"[{index}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,"
            f"volume={max(0.0, min(2.0, volume)):.3f},adelay={delay}|{delay}[{label}]"
        )
        labels.append(f"[{label}]")
    filters.append(
        f"{''.join(labels)}amix=inputs={len(labels)}:duration=first:dropout_transition=1,loudnorm[outa]"
    )
    run_ffmpeg([
        *arguments,
        "-filter_complex", ";".join(filters),
        "-map", "[outa]",
        "-codec:a", "libmp3lame", "-b:a", "192k",
        str(destination),
    ])


def analyze_audio(source: Path) -> dict[str, float | bool | None]:
    executable = shutil.which("ffmpeg")
    if not executable:
        raise MediaError("FFmpeg is required for audio validation.")
    result = subprocess.run(
        [executable, "-i", str(source), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True,
        text=True,
        check=False,
    )
    stderr = result.stderr
    mean_volume = _volume_value(stderr, "mean_volume")
    max_volume = _volume_value(stderr, "max_volume")
    return {
        "duration_seconds": round(probe_duration(source), 3),
        "mean_volume_db": mean_volume,
        "max_volume_db": max_volume,
        "clipping_risk": bool(max_volume is not None and max_volume > -0.2),
    }


def _volume_value(output: str, name: str) -> float | None:
    import re

    match = re.search(rf"{name}:\s*(-?inf|-?[0-9.]+)\s*dB", output)
    if not match or match.group(1) == "-inf":
        return None
    return round(float(match.group(1)), 3)
