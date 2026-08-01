"""Low-VRAM LTX-Video adapter with an optional external Q8 backend."""

from __future__ import annotations

import gc
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

from PIL import Image

from app.core.adapters import ModelSpec, ProgressCallback
from app.runtime.hardware import release_gpu_cache
from app.utils.files import MediaError, existing_file, media_output_dir, output_response, unique_path


class LtxVideoAdapter:
    def __init__(self, spec: ModelSpec):
        self.spec = spec
        self.model_id = spec.id
        self.pipeline: Any = None
        self.pipeline_mode: str | None = None
        self.torch: Any = None
        self.external_repo: Path | None = None
        self.external_python: str = sys.executable

    def load(self) -> None:
        repo_value = os.getenv(
            str(self.spec.options.get("external_repo_env", "LTX_Q8_REPO_PATH")), ""
        ).strip()
        entrypoint = str(self.spec.options.get("external_entrypoint", "inference.py"))
        if repo_value:
            candidate = Path(repo_value).expanduser().resolve()
            if (candidate / entrypoint).is_file():
                self.external_repo = candidate
        self.external_python = os.getenv(
            str(self.spec.options.get("external_python_env", "LTX_Q8_PYTHON")),
            sys.executable,
        )

        if self.external_repo is not None:
            return
        try:
            import torch
            import diffusers  # noqa: F401
        except ImportError as exc:
            raise MediaError(
                "LTX-Video is optional. Install `requirements-video.txt`, or configure "
                "LTX_Q8_REPO_PATH and LTX_Q8_PYTHON for the external Q8 environment."
            ) from exc
        if not torch.cuda.is_available():
            raise MediaError("LTX-Video requires a CUDA-capable NVIDIA GPU.")
        self.torch = torch

    def run(self, payload: dict[str, Any], progress: ProgressCallback) -> dict[str, Any]:
        prompt = str(payload.get("prompt", "")).strip()
        if not prompt:
            raise MediaError("LTX-Video requires a non-empty prompt.")

        requested = self._settings(payload)
        destination = unique_path(
            media_output_dir("video", payload.get("project")),
            payload.get("name", "ltx-video"),
            ".mp4",
        )
        input_path = payload.get("input_path")

        if self.external_repo is not None and not input_path:
            progress(10, "Running external LTX Q8 text-to-video")
            result = self._run_external_q8(prompt, payload, requested, destination)
            progress(95, "Saving LTX Q8 video")
            return result

        actual = dict(requested)
        retry_used = False
        try:
            self._run_diffusers(prompt, payload, actual, destination, progress)
        except Exception as exc:
            if not _is_oom(exc) or not bool(payload.get("allow_low_vram_retry", True)):
                raise
            retry_used = True
            self.unload()
            release_gpu_cache()
            actual = self._fallback_settings(actual)
            progress(20, "Retrying LTX with the low-VRAM profile")
            self._run_diffusers(prompt, payload, actual, destination, progress)

        response = output_response("video", "generate", destination, self.model_id).model_dump()
        response.update(
            {
                "backend": "diffusers-fp8-offload",
                "requested": requested,
                "actual": actual,
                "retry_used": retry_used,
                "seed": int(payload.get("seed", 42)),
                "mode": "image-to-video" if input_path else "text-to-video",
            }
        )
        return response

    def unload(self) -> None:
        self.pipeline = None
        self.pipeline_mode = None
        gc.collect()
        release_gpu_cache()
        self.torch = None

    def _run_external_q8(
        self,
        prompt: str,
        payload: dict[str, Any],
        settings: dict[str, int],
        destination: Path,
    ) -> dict[str, Any]:
        assert self.external_repo is not None
        transformer = str(
            payload.get(
                "q8_transformer",
                self.spec.options.get("q8_transformer", "sayakpaul/q8-ltx-video"),
            )
        )
        entrypoint = str(self.spec.options.get("external_entrypoint", "inference.py"))
        command = [
            self.external_python,
            str(self.external_repo / entrypoint),
            "--prompt",
            prompt,
            "--negative_prompt",
            str(payload.get("negative_prompt", _DEFAULT_NEGATIVE)),
            "--q8_transformer_path",
            transformer,
            "--num_frames",
            str(settings["num_frames"]),
            "--resolution",
            f"{settings['height']}x{settings['width']}",
            "--steps",
            str(settings["steps"]),
            "--max_sequence_length",
            str(int(payload.get("max_sequence_length", 256))),
            "--out_path",
            str(destination),
        ]
        result = subprocess.run(
            command,
            cwd=self.external_repo,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0 or not destination.is_file():
            lines = (result.stderr or result.stdout).strip().splitlines()
            detail = lines[-1] if lines else "External LTX Q8 generation failed."
            raise MediaError(detail)
        match = re.search(r"Max memory:\s*([0-9.]+)\s*MB", result.stdout)
        response = output_response("video", "generate", destination, self.model_id).model_dump()
        response.update(
            {
                "backend": "external-q8-kernels",
                "requested": settings,
                "actual": settings,
                "retry_used": False,
                "mode": "text-to-video",
                "reported_peak_vram_mb": float(match.group(1)) if match else None,
                "seed": None,
            }
        )
        return response

    def _run_diffusers(
        self,
        prompt: str,
        payload: dict[str, Any],
        settings: dict[str, int],
        destination: Path,
        progress: ProgressCallback,
    ) -> None:
        input_path = payload.get("input_path")
        mode = "image-to-video" if input_path else "text-to-video"
        pipe = self._get_diffusers_pipeline(mode, progress)
        torch = self.torch
        if torch is None:
            import torch as imported_torch
            torch = imported_torch
            self.torch = torch

        kwargs: dict[str, Any] = {
            "prompt": prompt,
            "negative_prompt": str(payload.get("negative_prompt", _DEFAULT_NEGATIVE)),
            "width": settings["width"],
            "height": settings["height"],
            "num_frames": settings["num_frames"],
            "num_inference_steps": settings["steps"],
            "generator": torch.Generator(device="cpu").manual_seed(int(payload.get("seed", 42))),
        }
        if input_path:
            image = Image.open(existing_file(str(input_path))).convert("RGB")
            kwargs["image"] = image.resize(
                (settings["width"], settings["height"]), Image.Resampling.LANCZOS
            )

        progress(45, f"Generating LTX {mode}")
        with torch.inference_mode():
            frames = pipe(**kwargs).frames[0]
        progress(88, "Encoding generated frames")
        from diffusers.utils import export_to_video
        export_to_video(frames, str(destination), fps=settings["fps"])

    def _get_diffusers_pipeline(self, mode: str, progress: ProgressCallback) -> Any:
        if self.pipeline is not None and self.pipeline_mode == mode:
            return self.pipeline
        self.pipeline = None
        release_gpu_cache()

        try:
            import torch
            from diffusers import AutoModel, LTXImageToVideoPipeline, LTXPipeline
        except ImportError as exc:
            raise MediaError("Install `requirements-video.txt` for the Diffusers LTX backend.") from exc

        self.torch = torch
        model_name = str(self.spec.options.get("base_model", "Lightricks/LTX-Video"))
        progress(5, "Loading the LTX transformer")
        transformer = AutoModel.from_pretrained(
            model_name,
            subfolder="transformer",
            torch_dtype=torch.bfloat16,
        )
        if hasattr(transformer, "enable_layerwise_casting") and hasattr(torch, "float8_e4m3fn"):
            transformer.enable_layerwise_casting(
                storage_dtype=torch.float8_e4m3fn,
                compute_dtype=torch.bfloat16,
            )

        pipeline_class = LTXImageToVideoPipeline if mode == "image-to-video" else LTXPipeline
        pipe = pipeline_class.from_pretrained(
            model_name,
            transformer=transformer,
            torch_dtype=torch.bfloat16,
        )
        if hasattr(pipe.vae, "enable_tiling"):
            pipe.vae.enable_tiling()
        _enable_offloading(pipe, torch)
        self.pipeline = pipe
        self.pipeline_mode = mode
        progress(18, "LTX model loaded with low-VRAM offloading")
        return pipe

    def _settings(self, payload: dict[str, Any]) -> dict[str, int]:
        options = self.spec.options
        width = _multiple_of_32(int(payload.get("width", options.get("width", 576))))
        height = _multiple_of_32(int(payload.get("height", options.get("height", 320))))
        if width * height > int(options.get("max_pixels", 337_920)):
            raise MediaError("Requested LTX resolution exceeds the configured 8GB pixel budget.")
        frames = _valid_frames(
            int(payload.get("num_frames", payload.get("frames", options.get("num_frames", 65))))
        )
        return {
            "width": width,
            "height": height,
            "num_frames": frames,
            "steps": max(4, min(50, int(payload.get("steps", options.get("steps", 20))))),
            "fps": max(8, min(30, int(payload.get("fps", options.get("fps", 24))))),
        }

    @staticmethod
    def _fallback_settings(settings: dict[str, int]) -> dict[str, int]:
        return {
            **settings,
            "width": min(settings["width"], 512),
            "height": min(settings["height"], 288),
            "num_frames": min(settings["num_frames"], 49),
            "steps": min(settings["steps"], 16),
        }


def _enable_offloading(pipe: Any, torch: Any) -> None:
    try:
        from diffusers.hooks import apply_group_offloading
        onload = torch.device("cuda")
        offload = torch.device("cpu")
        pipe.transformer.enable_group_offload(
            onload_device=onload,
            offload_device=offload,
            offload_type="leaf_level",
            use_stream=False,
        )
        apply_group_offloading(
            pipe.text_encoder,
            onload_device=onload,
            offload_device=offload,
            offload_type="block_level",
            num_blocks_per_group=2,
        )
        apply_group_offloading(
            pipe.vae,
            onload_device=onload,
            offload_device=offload,
            offload_type="leaf_level",
        )
    except (ImportError, AttributeError, TypeError):
        pipe.enable_model_cpu_offload()


def _multiple_of_32(value: int) -> int:
    return max(256, min(768, int(round(value / 32)) * 32))


def _valid_frames(value: int) -> int:
    value = max(9, min(121, value))
    return 1 + 8 * round((value - 1) / 8)


def _is_oom(exc: Exception) -> bool:
    return "out of memory" in str(exc).lower() or exc.__class__.__name__ == "OutOfMemoryError"


_DEFAULT_NEGATIVE = "worst quality, inconsistent motion, blurry, jittery, distorted, watermark, text"
