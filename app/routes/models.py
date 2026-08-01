from fastapi import APIRouter

from app.models import ModelView
from app.runtime.state import models, registry

router = APIRouter(prefix="/models", tags=["models"])


@router.get("", response_model=list[ModelView])
def list_models() -> list[ModelView]:
    return [
        ModelView(
            id=spec.id,
            capability=spec.capability,
            description=spec.description,
            implemented=spec.implemented,
            recommended=spec.recommended,
            available=registry.is_available(spec),
            active=models.active_id == spec.id,
            vram_gb=spec.vram_gb,
            dependency_group=spec.dependency_group,
            notes=spec.notes,
        )
        for spec in registry.list()
    ]


@router.get("/active")
def active_model() -> dict[str, str | None]:
    return {"model": models.active_id}


@router.post("/unload")
def unload_model() -> dict[str, str | None]:
    previous = models.active_id
    models.unload()
    return {"unloaded": previous}
