"""Persistent Bark text-to-audio adapter."""

from __future__ import annotations

import gc
from typing import Any

from app.core.adapters import ModelSpec, ProgressCallback
from app.utils.files import MediaError, media_output_dir, output_response, unique_path


class BarkAdapter:
    def __init__(self, spec: ModelSpec):
        self.spec = spec
        self.model_id = spec.id
        self.generator: Any = None
        self.numpy: Any = None
        self.wavfile: Any = None
        self.torch: Any = None

    def load(self) -> None:
        if self.generator is not None:
            return
        try:
            import numpy as np
            import scipy.io.wavfile
            import torch
            from transformers import pipeline
        except ImportError as exc:
            raise MediaError("Bark is optional. Install `requirements-bark.txt` and a compatible torch build.") from exc
        device = self.spec.options.get("device", "auto")
        if device == "cuda" and not torch.cuda.is_available():
            raise MediaError("CUDA was requested, but PyTorch cannot detect a CUDA device.")
        pipeline_device = -1 if device == "cpu" else (0 if torch.cuda.is_available() else -1)
        self.generator = pipeline("text-to-audio", model=self.spec.options.get("model", "suno/bark-small"), device=pipeline_device)
        self.numpy = np
        self.wavfile = scipy.io.wavfile
        self.torch = torch

    def run(self, payload: dict[str, Any], progress: ProgressCallback) -> dict[str, Any]:
        text = str(payload.get("text", "")).strip()
        if not text:
            raise MediaError("Bark requires a non-empty text value.")
        progress(10, "Generating Bark audio")
        result = self.generator(text)
        audio = self.numpy.asarray(result["audio"]).squeeze()
        destination = unique_path(media_output_dir("audio", payload.get("project")), payload.get("name", "bark-audio"), ".wav")
        self.wavfile.write(str(destination), result["sampling_rate"], audio)
        progress(95, "Saving audio")
        return output_response("audio", "tts", destination, self.model_id).model_dump()

    def unload(self) -> None:
        self.generator = None
        self.numpy = None
        self.wavfile = None
        gc.collect()
        if self.torch is not None and self.torch.cuda.is_available():
            self.torch.cuda.empty_cache()
        self.torch = None
