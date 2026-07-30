"""Dependency-free demo audio provider."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
import struct
import wave

from config import AudioConfig


class DemoAudioProvider:
    """Create a deterministic WAV tone so the full workflow can be tested locally."""

    file_extension = ".wav"

    def generate(self, prompt: str, output_path: Path, config: AudioConfig) -> Path:
        if not prompt.strip():
            raise ValueError("A prompt is required.")

        digest = hashlib.sha256(prompt.encode("utf-8")).digest()
        frequency = 220 + int.from_bytes(digest[:2], "big") % 440
        amplitude = 0.25
        frame_count = int(config.sample_rate * config.duration_seconds)

        with wave.open(str(output_path), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(2)
            audio.setframerate(config.sample_rate)

            for index in range(frame_count):
                fade = min(1.0, index / max(1, config.sample_rate // 20))
                remaining = frame_count - index
                fade *= min(1.0, remaining / max(1, config.sample_rate // 20))
                sample = amplitude * fade * math.sin(
                    2 * math.pi * frequency * index / config.sample_rate
                )
                audio.writeframes(struct.pack("<h", int(sample * 32767)))

        return output_path
