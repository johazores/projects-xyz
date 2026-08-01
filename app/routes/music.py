from fastapi import APIRouter

from app.models import ExpressiveSpeechRequest, JobView, MusicGenerateRequest, SoundEffectRequest
from app.runtime.state import registry, worker
from app.utils.files import MediaError

router = APIRouter(prefix="/audio-ai", tags=["audio-ai"])


def _submit(model_id: str, payload: dict) -> JobView:
    spec = registry.get(model_id)
    if not spec.implemented:
        raise MediaError(f"Model {model_id} is planned but not implemented yet.")
    return worker.submit("model", model_id, payload)


@router.post("/speech", response_model=JobView, status_code=202)
def generate_expressive_speech(request: ExpressiveSpeechRequest) -> JobView:
    payload = request.model_dump(exclude={"model"}, exclude_none=True)
    return _submit(request.model, payload)


@router.post("/music", response_model=JobView, status_code=202)
def generate_music(request: MusicGenerateRequest) -> JobView:
    payload = request.model_dump(exclude={"model"}, exclude_none=True)
    return _submit(request.model, payload)


@router.post("/sound-effect", response_model=JobView, status_code=202)
def generate_sound_effect(request: SoundEffectRequest) -> JobView:
    payload = request.model_dump(exclude={"model"}, exclude_none=True)
    return _submit(request.model, payload)
