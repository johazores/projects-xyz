"""Optional Bark text-to-audio provider."""

from __future__ import annotations

from pathlib import Path

from config import AudioConfig


class BarkAudioProvider:
    """Generate audio through a Transformers text-to-audio pipeline."""

    file_extension = ".wav"

    def generate(self, prompt: str, output_path: Path, config: AudioConfig) -> Path:
        if not prompt.strip():
            raise ValueError("A prompt is required.")

        try:
            import numpy as np
            import scipy.io.wavfile
            import torch
            from transformers import pipeline
        except ImportError as exc:
            raise RuntimeError(
                "Bark dependencies are missing. Install requirements-ai.txt and a compatible torch build."
            ) from exc

        device = self._resolve_device(config.device, torch)
        generator = pipeline(
            task="text-to-audio",
            model=config.model,
            device=device,
        )
        result = generator(prompt)
        audio = np.asarray(result["audio"]).squeeze()
        scipy.io.wavfile.write(str(output_path), result["sampling_rate"], audio)
        return output_path

    @staticmethod
    def _resolve_device(device: str, torch: object) -> int:
        if device == "cpu":
            return -1
        if device == "cuda":
            if not torch.cuda.is_available():
                raise RuntimeError("CUDA was requested, but PyTorch cannot detect a CUDA device.")
            return 0
        return 0 if torch.cuda.is_available() else -1
