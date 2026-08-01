from fastapi import APIRouter

from app.models import ImageBackgroundRequest, ImageBatchRequest, ImageGenerateRequest, JobView
from app.runtime.state import registry, worker
from app.services.image import apply_preset, list_presets
from app.utils.files import MediaError

router = APIRouter(prefix="/image", tags=["image"])


@router.get("/presets")
def presets() -> dict[str, dict[str, str]]:
    return list_presets()


@router.post("/generate", response_model=JobView, status_code=202)
def generate(request: ImageGenerateRequest) -> JobView:
    _validate_model(request.model)
    prompt, negative = apply_preset(request.prompt, request.negative_prompt, request.preset)
    payload = request.model_dump(exclude={"model", "preset"}, exclude_none=True)
    payload["prompt"] = prompt
    payload["negative_prompt"] = negative or ""
    return worker.submit("model", request.model, payload)


@router.post("/generate-batch", response_model=list[JobView], status_code=202)
def generate_batch(request: ImageBatchRequest) -> list[JobView]:
    _validate_model(request.model)
    jobs: list[JobView] = []
    for index, value in enumerate(request.prompts):
        if not value.strip():
            continue
        prompt, negative = apply_preset(value, request.negative_prompt, request.preset)
        payload = request.model_dump(exclude={"model", "preset", "prompts"}, exclude_none=True)
        payload.update(
            {
                "prompt": prompt,
                "negative_prompt": negative or "",
                "count": 1,
                "seed": request.seed + index if request.seed is not None else None,
            }
        )
        jobs.append(worker.submit("model", request.model, payload))
    if not jobs:
        raise MediaError("At least one non-empty prompt is required.")
    return jobs


@router.post("/remove-background", response_model=JobView, status_code=202)
def remove_background(request: ImageBackgroundRequest) -> JobView:
    _validate_model(request.model)
    return worker.submit(
        "model",
        request.model,
        request.model_dump(exclude={"model"}, exclude_none=True),
    )


def _validate_model(model_id: str) -> None:
    spec = registry.get(model_id)
    if not spec.implemented:
        raise MediaError(f"Model {model_id} is planned but not implemented yet.")
