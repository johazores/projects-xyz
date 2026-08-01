"""BiRefNet Lite background removal adapter for subject cutouts."""

from __future__ import annotations

import gc
from typing import Any

from PIL import Image

from app.core.adapters import ModelSpec, ProgressCallback
from app.utils.files import MediaError, existing_file, media_output_dir, output_response, unique_path


class BiRefNetAdapter:
    def __init__(self, spec: ModelSpec):
        self.spec = spec
        self.model_id = spec.id
        self.model: Any = None
        self.transform: Any = None
        self.to_pil: Any = None
        self.torch: Any = None
        self.device = "cpu"

    def load(self) -> None:
        if self.model is not None:
            return
        try:
            import torch
            from torchvision import transforms
            from transformers import AutoModelForImageSegmentation
        except ImportError as exc:
            raise MediaError(
                "BiRefNet is optional. Install `requirements-vision.txt`."
            ) from exc

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        model_name = self.spec.options.get("model", "ZhengPeng7/BiRefNet_lite")
        model = AutoModelForImageSegmentation.from_pretrained(
            model_name, trust_remote_code=True
        )
        model.to(self.device)
        model.eval()
        if self.device == "cuda":
            model.half()

        resolution = int(self.spec.options.get("resolution", 1024))
        self.transform = transforms.Compose(
            [
                transforms.Resize((resolution, resolution)),
                transforms.ToTensor(),
                transforms.Normalize(
                    [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
                ),
            ]
        )
        self.to_pil = transforms.ToPILImage()
        self.model = model
        self.torch = torch

    def run(self, payload: dict[str, Any], progress: ProgressCallback) -> dict[str, Any]:
        source = existing_file(str(payload.get("input_path", "")))
        image = Image.open(source).convert("RGBA")
        rgb = image.convert("RGB")
        progress(20, "Segmenting foreground subject")

        tensor = self.transform(rgb).unsqueeze(0).to(self.device)
        if self.device == "cuda":
            tensor = tensor.half()
        with self.torch.inference_mode():
            predictions = self.model(tensor)[-1].sigmoid().cpu()
        mask = self.to_pil(predictions[0].squeeze()).resize(
            image.size, Image.Resampling.LANCZOS
        )
        image.putalpha(mask)

        destination = unique_path(
            media_output_dir("image", payload.get("project")),
            payload.get("name", f"{source.stem}-cutout"),
            ".png",
        )
        image.save(destination)
        progress(95, "Saving transparent subject")
        return output_response(
            "image", "remove-background", destination, self.model_id
        ).model_dump()

    def unload(self) -> None:
        self.model = None
        self.transform = None
        self.to_pil = None
        gc.collect()
        if self.torch is not None and self.torch.cuda.is_available():
            self.torch.cuda.empty_cache()
        self.torch = None
        self.device = "cpu"
