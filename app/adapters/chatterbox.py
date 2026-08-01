"""Expressive Chatterbox TTS with consent enforcement for cloned voices."""

from __future__ import annotations

import gc
from typing import Any

from app.config import settings
from app.core.adapters import ModelSpec, ProgressCallback
from app.runtime.voice_consent import VoiceConsentStore
from app.utils.files import MediaError, existing_file, media_output_dir, output_response, unique_path


class ChatterboxAdapter:
    def __init__(self, spec: ModelSpec):
        self.spec = spec
        self.model_id = spec.id
        self.model: Any = None
        self.torchaudio: Any = None
        self.torch: Any = None
        self.mode = str(spec.options.get("mode", "turbo"))

    def load(self) -> None:
        if self.model is not None:
            return
        try:
            import torch
            import torchaudio
            if self.mode in {"turbo", "nano"}:
                from chatterbox.tts_turbo import ChatterboxTurboTTS
                self.model = ChatterboxTurboTTS.from_pretrained(
                    device="cuda" if torch.cuda.is_available() else "cpu",
                    nano=self.mode == "nano",
                )
            elif self.mode == "multilingual-v3":
                from chatterbox.mtl_tts import ChatterboxMultilingualTTS
                self.model = ChatterboxMultilingualTTS.from_pretrained(
                    device="cuda" if torch.cuda.is_available() else "cpu",
                    t3_model="v3",
                )
            else:
                from chatterbox.tts import ChatterboxTTS
                self.model = ChatterboxTTS.from_pretrained(
                    device="cuda" if torch.cuda.is_available() else "cpu"
                )
        except ImportError as exc:
            raise MediaError(
                "Chatterbox is optional. Install `requirements-voices.txt` in a Python 3.11 environment."
            ) from exc
        self.torch = torch
        self.torchaudio = torchaudio

    def run(self, payload: dict[str, Any], progress: ProgressCallback) -> dict[str, Any]:
        text = str(payload.get("text", "")).strip()
        if not text:
            raise MediaError("Chatterbox requires non-empty text.")

        reference_value = payload.get("reference_path")
        reference_path = None
        consent = None
        if reference_value:
            reference_path = existing_file(str(reference_value))
            consent = VoiceConsentStore(settings.voice_consents_path).require(
                payload.get("consent_id"), reference_path
            )
        elif self.mode in {"turbo", "nano"}:
            raise MediaError("Chatterbox Turbo and Nano require reference_path and consent_id.")

        progress(15, "Preparing expressive speech")
        kwargs: dict[str, Any] = {}
        if reference_path:
            kwargs["audio_prompt_path"] = str(reference_path)
        if self.mode == "multilingual-v3":
            kwargs["language_id"] = str(payload.get("language", "en"))
        else:
            if payload.get("exaggeration") is not None:
                kwargs["exaggeration"] = float(payload["exaggeration"])
            if payload.get("cfg_weight") is not None:
                kwargs["cfg_weight"] = float(payload["cfg_weight"])

        waveform = self.model.generate(text, **kwargs)
        if getattr(waveform, "ndim", 0) == 1:
            waveform = waveform.unsqueeze(0)
        destination = unique_path(
            media_output_dir("audio", payload.get("project")),
            payload.get("name", "chatterbox-speech"),
            ".wav",
        )
        self.torchaudio.save(str(destination), waveform.cpu(), int(self.model.sr))
        progress(95, "Saving expressive speech")
        result = output_response("audio", "tts", destination, self.model_id).model_dump()
        result.update(
            {
                "mode": self.mode,
                "language": payload.get("language", "en"),
                "voice_consent_id": consent.get("id") if consent else None,
            }
        )
        return result

    def unload(self) -> None:
        self.model = None
        self.torchaudio = None
        gc.collect()
        if self.torch is not None and self.torch.cuda.is_available():
            self.torch.cuda.empty_cache()
        self.torch = None
