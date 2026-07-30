"""Local speech-to-text helpers using the optional faster-whisper package."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Protocol


class Segment(Protocol):
    start: float
    end: float
    text: str


def transcribe_audio(
    input_path: Path,
    output_path: Path,
    *,
    model_name: str,
    device: str,
    compute_type: str,
    language: str | None,
    output_format: str,
) -> Path:
    """Transcribe one local audio or video file to plain text or SRT."""

    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "Transcription requires faster-whisper. "
            "Install it with: pip install -r requirements-transcription.txt"
        ) from exc

    model = WhisperModel(model_name, device=device, compute_type=compute_type)
    segments, _ = model.transcribe(
        str(input_path),
        language=language,
        vad_filter=True,
        log_progress=True,
    )
    collected = list(segments)

    if output_format == "txt":
        content = "\n".join(
            segment.text.strip() for segment in collected if segment.text.strip()
        )
    elif output_format == "srt":
        content = _build_srt(collected)
    else:
        raise ValueError("output_format must be txt or srt.")

    output_path.write_text(content.rstrip() + "\n", encoding="utf-8")
    return output_path


def _build_srt(segments: Iterable[Segment]) -> str:
    blocks = []
    subtitle_number = 1
    for segment in segments:
        text = segment.text.strip()
        if not text:
            continue
        blocks.append(
            f"{subtitle_number}\n{_timestamp(segment.start)} --> {_timestamp(segment.end)}\n{text}"
        )
        subtitle_number += 1
    return "\n\n".join(blocks)


def _timestamp(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
