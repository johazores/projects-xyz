"""Real-ESRGAN NCNN adapter for stable tiled local upscaling."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
from typing import Any

from app.core.adapters import ModelSpec, ProgressCallback
from app.utils.files import MediaError, existing_file, media_output_dir, output_response, unique_path


class RealEsrganNcnnAdapter:
    def __init__(self, spec: ModelSpec):
        self.spec = spec
        self.model_id = spec.id
        self.executable: str | None = None

    def load(self) -> None:
        configured = os.getenv("REALESRGAN_NCNN_PATH") or self.spec.options.get(
            "executable"
        )
        candidates = [
            configured,
            self.spec.executable,
            "realesrgan-ncnn-vulkan",
            "realesrgan-ncnn-vulkan.exe",
        ]
        for candidate in candidates:
            if not candidate:
                continue
            path = Path(str(candidate)).expanduser()
            if path.is_file():
                self.executable = str(path.resolve())
                return
            found = shutil.which(str(candidate))
            if found:
                self.executable = found
                return
        raise MediaError(
            "Real-ESRGAN NCNN executable was not found. Set REALESRGAN_NCNN_PATH or add it to PATH."
        )

    def run(self, payload: dict[str, Any], progress: ProgressCallback) -> dict[str, Any]:
        source = existing_file(str(payload.get("input_path", "")))
        scale = int(payload.get("scale", self.spec.options.get("scale", 2)))
        if scale not in {2, 3, 4}:
            raise MediaError("Real-ESRGAN scale must be 2, 3, or 4.")
        model_name = str(
            payload.get(
                "model_name", self.spec.options.get("model_name", "realesrgan-x4plus")
            )
        )
        tile = int(payload.get("tile", self.spec.options.get("tile", 256)))
        destination = unique_path(
            media_output_dir("image", payload.get("project")),
            payload.get("name", f"{source.stem}-upscaled"),
            ".png",
        )
        progress(10, "Upscaling image with Real-ESRGAN")
        result = subprocess.run(
            [
                str(self.executable),
                "-i",
                str(source),
                "-o",
                str(destination),
                "-n",
                model_name,
                "-s",
                str(scale),
                "-t",
                str(tile),
                "-f",
                "png",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0 or not destination.is_file():
            detail = (
                result.stderr or result.stdout or "Real-ESRGAN failed."
            ).strip().splitlines()
            raise MediaError(detail[-1] if detail else "Real-ESRGAN failed.")
        progress(95, "Saving upscaled image")
        output = output_response(
            "image", "upscale", destination, self.model_id
        ).model_dump()
        output.update({"scale": scale, "model_name": model_name, "tile": tile})
        return output

    def unload(self) -> None:
        self.executable = None
