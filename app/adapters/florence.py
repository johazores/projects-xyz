"""Florence-2 image captioning, OCR, and grounding adapter."""

from __future__ import annotations

import gc
from typing import Any

from PIL import Image

from app.core.adapters import ModelSpec, ProgressCallback
from app.utils.files import MediaError, existing_file

_ALLOWED_TASKS = {
    "<CAPTION>",
    "<DETAILED_CAPTION>",
    "<MORE_DETAILED_CAPTION>",
    "<OCR>",
    "<OCR_WITH_REGION>",
    "<OD>",
    "<DENSE_REGION_CAPTION>",
}


class FlorenceAdapter:
    def __init__(self, spec: ModelSpec):
        self.spec = spec
        self.model_id = spec.id
        self.model: Any = None
        self.processor: Any = None
        self.torch: Any = None

    def load(self) -> None:
        if self.model is not None:
            return
        try:
            import torch
            from transformers import AutoProcessor, Florence2ForConditionalGeneration
        except ImportError as exc:
            raise MediaError(
                "Florence-2 is optional. Install `requirements-vision.txt`."
            ) from exc
        model_name = self.spec.options.get(
            "model", "florence-community/Florence-2-large"
        )
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.model = Florence2ForConditionalGeneration.from_pretrained(
            model_name, torch_dtype=dtype
        )
        self.model.to("cuda" if torch.cuda.is_available() else "cpu")
        self.model.eval()
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.torch = torch

    def run(self, payload: dict[str, Any], progress: ProgressCallback) -> dict[str, Any]:
        source = existing_file(str(payload.get("input_path", "")))
        task = str(payload.get("task", "<DETAILED_CAPTION>")).upper()
        if task not in _ALLOWED_TASKS:
            raise MediaError(f"Unsupported Florence task: {task}")
        image = Image.open(source).convert("RGB")
        progress(15, f"Running Florence task {task}")
        inputs = self.processor(text=task, images=image, return_tensors="pt")
        inputs = {name: tensor.to(self.model.device) for name, tensor in inputs.items()}
        if "pixel_values" in inputs:
            inputs["pixel_values"] = inputs["pixel_values"].to(self.model.dtype)
        max_new_tokens = max(
            16, min(1024, int(payload.get("max_new_tokens", 512)))
        )
        num_beams = max(1, min(5, int(payload.get("num_beams", 3))))
        with self.torch.inference_mode():
            generated = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                num_beams=num_beams,
            )
        raw = self.processor.batch_decode(
            generated,
            skip_special_tokens=False,
        )[0]
        parsed = self.processor.post_process_generation(
            raw, task=task, image_size=image.size
        )
        progress(95, "Florence analysis completed")
        return {
            "model": self.model_id,
            "input_path": str(source),
            "task": task,
            "raw": raw,
            "result": parsed,
            "caption": _caption_text(parsed, task),
        }

    def unload(self) -> None:
        self.model = None
        self.processor = None
        gc.collect()
        if self.torch is not None and self.torch.cuda.is_available():
            self.torch.cuda.empty_cache()
        self.torch = None


def _caption_text(parsed: Any, task: str) -> str | None:
    if isinstance(parsed, dict):
        value = parsed.get(task)
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            for key in ("caption", "text", "labels"):
                candidate = value.get(key)
                if isinstance(candidate, str):
                    return candidate
                if isinstance(candidate, list):
                    return ", ".join(str(item) for item in candidate)
    return None
