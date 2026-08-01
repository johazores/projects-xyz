"""Persistent faster-whisper adapter for transcripts and subtitles."""

from __future__ import annotations

import gc
from typing import Any

from app.core.adapters import ModelSpec, ProgressCallback
from app.utils.files import MediaError, existing_file, media_output_dir, output_response, unique_path
from app.utils.transcription import transcribe_with_model


class FasterWhisperAdapter:
    def __init__(self, spec: ModelSpec):
        self.spec = spec
        self.model_id = spec.id
        self.model: Any = None

    def load(self) -> None:
        if self.model is not None:
            return
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise MediaError("faster-whisper is optional. Install `requirements-speech.txt`.") from exc
        self.model = WhisperModel(
            self.spec.options.get("model", "large-v3-turbo"),
            device=self.spec.options.get("device", "cuda"),
            compute_type=self.spec.options.get("compute_type", "int8_float16"),
        )

    def run(self, payload: dict[str, Any], progress: ProgressCallback) -> dict[str, Any]:
        source = existing_file(str(payload.get("input_path", "")))
        output_format = str(payload.get("output_format", "srt")).lower()
        if output_format not in {"txt", "srt"}:
            raise MediaError("output_format must be txt or srt.")
        destination = unique_path(media_output_dir("audio", payload.get("project")), f"{source.stem}-transcript", f".{output_format}")
        progress(10, "Transcribing media")
        transcribe_with_model(self.model, source, destination, language=payload.get("language"), output_format=output_format)
        progress(95, "Saving transcript")
        return output_response("audio", "transcribe", destination, self.model_id).model_dump()

    def unload(self) -> None:
        self.model = None
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
