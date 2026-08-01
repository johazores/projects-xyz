"""SDXL inpainting with CPU offload and VAE tiling."""

from __future__ import annotations

import gc
import secrets
from typing import Any

from PIL import Image, ImageOps

from app.core.adapters import ModelSpec, ProgressCallback
from app.utils.files import MediaError, existing_file, media_output_dir, output_response, unique_path


class SdxlInpaintAdapter:
    def __init__(self, spec: ModelSpec):
        self.spec = spec
        self.model_id = spec.id
        self.pipe: Any = None
        self.torch: Any = None

    def load(self) -> None:
        if self.pipe is not None:
            return
        try:
            import torch
            from diffusers import AutoPipelineForInpainting
        except ImportError as exc:
            raise MediaError(
                "SDXL inpainting is optional. Install `requirements-image.txt`."
            ) from exc
        if not torch.cuda.is_available():
            raise MediaError(
                "SDXL inpainting requires CUDA for the supported local profile."
            )
        pipe = AutoPipelineForInpainting.from_pretrained(
            self.spec.options.get(
                "model", "diffusers/stable-diffusion-xl-1.0-inpainting-0.1"
            ),
            torch_dtype=torch.float16,
            variant="fp16",
            use_safetensors=True,
        )
        pipe.enable_model_cpu_offload()
        if hasattr(pipe, "enable_vae_tiling"):
            pipe.enable_vae_tiling()
        if hasattr(pipe, "enable_attention_slicing"):
            pipe.enable_attention_slicing()
        if hasattr(pipe, "set_progress_bar_config"):
            pipe.set_progress_bar_config(disable=True)
        self.pipe = pipe
        self.torch = torch

    def run(self, payload: dict[str, Any], progress: ProgressCallback) -> dict[str, Any]:
        source = existing_file(str(payload.get("input_path", "")))
        mask_path = existing_file(str(payload.get("mask_path", "")))
        prompt = str(payload.get("prompt", "")).strip()
        if not prompt:
            raise MediaError("SDXL inpainting requires a prompt.")
        image = Image.open(source).convert("RGB")
        mask = Image.open(mask_path).convert("L")
        target_size = (
            _floor_multiple(image.width, 8),
            _floor_multiple(image.height, 8),
        )
        image = ImageOps.fit(image, target_size, method=Image.Resampling.LANCZOS)
        mask = ImageOps.fit(mask, target_size, method=Image.Resampling.LANCZOS)
        seed = int(
            payload.get("seed")
            if payload.get("seed") is not None
            else secrets.randbelow(2_147_483_647)
        )
        steps = int(payload.get("steps", self.spec.options.get("steps", 30)))
        guidance = float(
            payload.get("guidance", self.spec.options.get("guidance", 7.0))
        )
        strength = float(
            payload.get("strength", self.spec.options.get("strength", 0.95))
        )
        progress(10, "Running SDXL inpainting")
        result = self.pipe(
            prompt=prompt,
            negative_prompt=str(
                payload.get(
                    "negative_prompt", "blurry, low quality, text, watermark"
                )
            ),
            image=image,
            mask_image=mask,
            num_inference_steps=steps,
            guidance_scale=guidance,
            strength=strength,
            generator=self.torch.Generator(device="cuda").manual_seed(seed),
        ).images[0]
        destination = unique_path(
            media_output_dir("image", payload.get("project")),
            payload.get("name", "inpainted"),
            ".png",
        )
        result.save(destination)
        progress(95, "Saving inpainted image")
        output = output_response(
            "image", "inpaint", destination, self.model_id
        ).model_dump()
        output.update(
            {
                "seed": seed,
                "steps": steps,
                "guidance": guidance,
                "strength": strength,
            }
        )
        return output

    def unload(self) -> None:
        self.pipe = None
        gc.collect()
        if self.torch is not None and self.torch.cuda.is_available():
            self.torch.cuda.empty_cache()
        self.torch = None


def _floor_multiple(value: int, multiple: int) -> int:
    return max(multiple, value - value % multiple)
