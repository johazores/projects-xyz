"""Stable Audio 3 local CLI adapter for small sound-effect generation."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
from typing import Any

from app.core.adapters import ModelSpec, ProgressCallback
from app.utils.files import MediaError, media_output_dir, output_response, unique_path


class StableAudioCliAdapter:
    def __init__(self, spec: ModelSpec):
        self.spec = spec
        self.model_id = spec.id
        self.executable: str | None = None

    def load(self) -> None:
        configured = os.getenv(str(self.spec.options.get("executable_env", "STABLE_AUDIO_CLI")))
        for candidate in (configured, self.spec.executable, "stable-audio"):
            if not candidate:
                continue
            path = Path(str(candidate)).expanduser()
            if path.is_file():
                self.executable = str(path.resolve())
                return
            resolved = shutil.which(str(candidate))
            if resolved:
                self.executable = resolved
                return
        raise MediaError(
            "Stable Audio 3 is optional. Install its official local CLI and set STABLE_AUDIO_CLI if needed."
        )

    def run(self, payload: dict[str, Any], progress: ProgressCallback) -> dict[str, Any]:
        prompt = str(payload.get("prompt", "")).strip()
        if not prompt:
            raise MediaError("Stable Audio requires a sound-effect prompt.")
        duration = max(0.5, min(120.0, float(payload.get("duration", 4))))
        destination = unique_path(
            media_output_dir("audio", payload.get("project")),
            payload.get("name", "sound-effect"),
            ".wav",
        )
        progress(10, "Generating sound effect on the local Stable Audio runtime")
        command = [
            str(self.executable),
            "--model",
            str(self.spec.options.get("model", "small-sfx")),
            "-p",
            prompt,
            "--duration",
            f"{duration:.3f}",
            "-o",
            str(destination),
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0 or not destination.is_file():
            lines = (result.stderr or result.stdout).strip().splitlines()
            raise MediaError(lines[-1] if lines else "Stable Audio generation failed.")
        progress(95, "Saving generated sound effect")
        response = output_response("audio", "sound-effect", destination, self.model_id).model_dump()
        response.update({"duration": duration, "backend": "stable-audio-cli"})
        return response

    def unload(self) -> None:
        self.executable = None
