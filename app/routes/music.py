from fastapi import APIRouter
from pydantic import Field

from app.models import ExpressiveSpeechRequest, JobView, MusicGenerateRequest, SoundEffectRequest
from app.runtime.state import audio_presets, registry, worker
from app.utils.files import MediaError

router = APIRouter(prefix="/audio-ai", tags=["audio-ai"])


class PresetMusicRequest(MusicGenerateRequest):
    preset: str | None = Field(default=None, max_length=120)


class PresetSoundEffectRequest(SoundEffectRequest):
    preset: str | None = Field(default=None, max_length=120)


def _submit(model_id: str, payload: dict) -> JobView:
    spec = registry.get(model_id)
    if not spec.implemented:
        raise MediaError(f"Model {model_id} is planned but not implemented yet.")
    return worker.submit("model", model_id, payload)


@router.get("/presets")
def list_audio_presets() -> dict:
    return audio_presets.list()


@router.post("/speech", response_model=JobView, status_code=202)
def generate_expressive_speech(request: ExpressiveSpeechRequest) -> JobView:
    return _submit(request.model, request.model_dump(exclude={"model"}, exclude_none=True))


@router.post("/music", response_model=JobView, status_code=202)
def generate_music(request: PresetMusicRequest) -> JobView:
    return _submit(request.model, request.model_dump(exclude={"model"}, exclude_none=True))


@router.post("/sound-effect", response_model=JobView, status_code=202)
def generate_sound_effect(request: PresetSoundEffectRequest) -> JobView:
    return _submit(request.model, request.model_dump(exclude={"model"}, exclude_none=True))
