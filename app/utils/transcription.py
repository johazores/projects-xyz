"""Optional local speech-to-text support."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Protocol

from app.utils.files import MediaError


class Segment(Protocol):
    start: float
    end: float
    text: str


def transcribe(
    source: Path,
    destination: Path,
    *,
    model_name: str,
    device: str,
    compute_type: str,
    language: str | None,
    output_format: str,
) -> None:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise MediaError(
            "Transcription is optional. Install it with `pip install -r requirements-local.txt`."
        ) from exc

    model = WhisperModel(model_name, device=device, compute_type=compute_type)
    segments, _ = model.transcribe(
        str(source), language=language, vad_filter=True, log_progress=True
    )
    collected = list(segments)

    if output_format == "txt":
        content = "\n".join(item.text.strip() for item in collected if item.text.strip())
    else:
        content = build_srt(collected)

    destination.write_text(content.rstrip() + "\n", encoding="utf-8")


def build_srt(segments: Iterable[Segment]) -> str:
    blocks: list[str] = []
    number = 1
    for segment in segments:
        text = segment.text.strip()
        if not text:
            continue
        blocks.append(
            f"{number}\n{timestamp(segment.start)} --> {timestamp(segment.end)}\n{text}"
        )
        number += 1
    return "\n\n".join(blocks)


def timestamp(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
