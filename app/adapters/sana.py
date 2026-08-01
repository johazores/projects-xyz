"""Sana 1.6B INT4 adapter tuned for a single 8GB NVIDIA GPU."""

from __future__ import annotations

import gc
import secrets
from typing import Any

from app.core.adapters import ModelSpec, ProgressCallback
from app.utils.files import MediaError, media_output_dir, output_response, unique_path


class SanaAdapter:
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
            from diffusers import SanaPipeline
            from nunchaku import NunchakuSanaTransformer2DModel
        except ImportError as exc:
            raise MediaError(
                "Sana INT4 is optional. Install `requirements-image.txt` and the matching Nunchaku build."
            ) from exc
        if not torch.cuda.is_available():
            raise MediaError("Sana INT4 requires a CUDA-capable NVIDIA GPU.")

        options = self.spec.options
        transformer = NunchakuSanaTransformer2DModel.from_pretrained(
            options.get(
                "transformer_model",
                "nunchaku-tech/nunchaku-sana/svdq-int4_r32-sana1.6b.safetensors",
            )
        )
        pipe = SanaPipeline.from_pretrained(
            options.get(
                "base_model",
                "Efficient-Large-Model/Sana_1600M_1024px_BF16_diffusers",
            ),
            transformer=transformer,
            variant=options.get("variant", "bf16"),
            torch_dtype=torch.bfloat16,
        ).to("cuda")
        pipe.text_encoder.to(torch.bfloat16)
        pipe.vae.to(torch.bfloat16)
        if hasattr(pipe.vae, "enable_tiling"):
            pipe.vae.enable_tiling()
        if hasattr(pipe, "set_progress_bar_config"):
            pipe.set_progress_bar_config(disable=True)
        self.pipe = pipe
        self.torch = torch

    def run(self, payload: dict[str, Any], progress: ProgressCallback) -> dict[str, Any]:
        prompt = str(payload.get("prompt", "")).strip()
        if not prompt:
            raise MediaError("Sana requires a non-empty prompt.")
        count = _int_value(payload, "count", 1, 1, 8)
        width = _multiple_of_32(
            payload, "width", self.spec.options.get("width", 1024), 512, 1536
        )
        height = _multiple_of_32(
            payload, "height", self.spec.options.get("height", 576), 320, 1024
        )
        max_pixels = int(self.spec.options.get("max_pixels", 1_048_576))
        if width * height > max_pixels:
            raise MediaError(
                f"Requested image is too large for the 8GB profile. Maximum pixels: {max_pixels}."
            )
        steps = _int_value(
            payload, "steps", self.spec.options.get("steps", 20), 1, 50
        )
        guidance = float(
            payload.get("guidance", self.spec.options.get("guidance", 4.5))
        )
        if not 1 <= guidance <= 15:
            raise MediaError("guidance must be between 1 and 15.")
        negative = str(payload.get("negative_prompt", ""))
        base_seed = int(
            payload.get("seed")
            if payload.get("seed") is not None
            else secrets.randbelow(2_147_483_647)
        )
        project = payload.get("project")
        name = str(payload.get("name", "sana-image"))
        outputs: list[dict[str, Any]] = []

        for index in range(count):
            seed = base_seed + index
            progress(
                5 + int(index / count * 85),
                f"Generating image {index + 1} of {count}",
            )
            generator = self.torch.Generator(device="cuda").manual_seed(seed)
            result = self.pipe(
                prompt=prompt,
                negative_prompt=negative,
                width=width,
                height=height,
                num_inference_steps=steps,
                guidance_scale=guidance,
                generator=generator,
            )
            image = result.images[0]
            destination = unique_path(
                media_output_dir("image", project), f"{name}-{index + 1}", ".png"
            )
            image.save(destination)
            item = output_response(
                "image", "generate", destination, self.model_id
            ).model_dump()
            item.update(
                {
                    "seed": seed,
                    "width": width,
                    "height": height,
                    "steps": steps,
                    "guidance": guidance,
                }
            )
            outputs.append(item)

        progress(95, "Saving generated images")
        return {
            "model": self.model_id,
            "prompt": prompt,
            "negative_prompt": negative,
            "base_seed": base_seed,
            "outputs": outputs,
        }

    def unload(self) -> None:
        self.pipe = None
        gc.collect()
        if self.torch is not None and self.torch.cuda.is_available():
            self.torch.cuda.empty_cache()
            if hasattr(self.torch.cuda, "ipc_collect"):
                self.torch.cuda.ipc_collect()
        self.torch = None


def _int_value(
    payload: dict[str, Any], key: str, default: int, minimum: int, maximum: int
) -> int:
    value = int(payload.get(key, default))
    if not minimum <= value <= maximum:
        raise MediaError(f"{key} must be between {minimum} and {maximum}.")
    return value


def _multiple_of_32(
    payload: dict[str, Any], key: str, default: int, minimum: int, maximum: int
) -> int:
    value = _int_value(payload, key, default, minimum, maximum)
    if value % 32:
        raise MediaError(f"{key} must be a multiple of 32.")
    return value
