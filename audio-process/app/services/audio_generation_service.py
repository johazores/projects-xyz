from pathlib import Path
import numpy as np
import scipy.io.wavfile
from app.core.config import Settings
from app.core.errors import AudioGenerationError


class AudioGenerationService:
    """
    Lazy-loads the AI model only when /audio/generate is called.
    This keeps app startup fast and avoids downloading the model until needed.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._pipeline = None

    def generate_from_text(self, text: str, output_path: Path) -> None:
        if not text.strip():
            raise AudioGenerationError("Text is required.")

        try:
            pipe = self._get_pipeline()
            output = pipe(text)

            audio = output["audio"]
            sampling_rate = output["sampling_rate"]

            # Some model outputs are shaped as (1, samples). Convert to plain 1D/2D array.
            audio_array = np.asarray(audio).squeeze()

            scipy.io.wavfile.write(
                str(output_path),
                rate=sampling_rate,
                data=audio_array,
            )
        except Exception as exc:
            raise AudioGenerationError(str(exc)) from exc

    def _get_pipeline(self):
        if self._pipeline is not None:
            return self._pipeline

        try:
            import torch
            from transformers import pipeline
        except ImportError as exc:
            raise AudioGenerationError(
                "Missing AI dependencies. Run: pip install torch torchaudio transformers scipy soundfile"
            ) from exc

        device = self._resolve_device(torch)

        self._pipeline = pipeline(
            task="text-to-audio",
            model=self.settings.ai_model_name,
            device=device,
        )

        return self._pipeline

    def _resolve_device(self, torch) -> int:
        if self.settings.ai_device == "cpu":
            return -1

        if self.settings.ai_device == "cuda":
            if not torch.cuda.is_available():
                raise AudioGenerationError("CUDA was requested, but PyTorch cannot detect your GPU.")
            return 0

        # auto mode
        return 0 if torch.cuda.is_available() else -1
