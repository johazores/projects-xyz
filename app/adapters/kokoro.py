"""Persistent Kokoro text-to-speech adapter."""

from __future__ import annotations

import gc
from typing import Any

from app.core.adapters import ModelSpec, ProgressCallback
from app.utils.files import MediaError, media_output_dir, output_response, unique_path


class KokoroAdapter:
    def __init__(self, spec: ModelSpec):
        self.spec = spec
        self.model_id = spec.id
        self.pipeline: Any = None
        self.soundfile: Any = None
        self.numpy: Any = None

    def load(self) -> None:
        if self.pipeline is not None:
            return
        try:
            import numpy as np
            import soundfile as sf
            from kokoro import KPipeline
        except ImportError as exc:
            raise MediaError("Kokoro is optional. Install `requirements-speech.txt` and espeak-ng.") from exc
        self.numpy = np
        self.soundfile = sf
        self.pipeline = KPipeline(lang_code=self.spec.options.get("lang_code", "a"))

    def run(self, payload: dict[str, Any], progress: ProgressCallback) -> dict[str, Any]:
        text = str(payload.get("text", "")).strip()
        if not text:
            raise MediaError("Kokoro requires a non-empty text value.")
        voice = str(payload.get("voice", self.spec.options.get("voice", "af_heart")))
        speed = float(payload.get("speed", 1.0))
        project = payload.get("project")
        progress(10, "Preparing Kokoro narration")
        chunks = []
        for _, _, audio in self.pipeline(text, voice=voice, speed=speed):
            chunks.append(self.numpy.asarray(audio))
            progress(min(85, 20 + len(chunks) * 10), "Generating speech")
        if not chunks:
            raise MediaError("Kokoro did not return any audio.")
        combined = self.numpy.concatenate(chunks)
        destination = unique_path(media_output_dir("audio", project), payload.get("name", "narration"), ".wav")
        self.soundfile.write(destination, combined, 24_000)
        progress(95, "Saving narration")
        return output_response("audio", "tts", destination, self.model_id).model_dump()

    def unload(self) -> None:
        self.pipeline = None
        self.soundfile = None
        self.numpy = None
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
