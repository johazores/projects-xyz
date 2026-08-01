from fastapi import APIRouter

from app.models import VoiceConsentCreate, VoiceConsentView
from app.runtime.state import voice_consents

router = APIRouter(prefix="/voices", tags=["voices"])


@router.get("/consents", response_model=list[VoiceConsentView])
def list_consents() -> list[dict]:
    return voice_consents.list()


@router.post("/consents", response_model=VoiceConsentView, status_code=201)
def create_consent(request: VoiceConsentCreate) -> dict:
    return voice_consents.create(**request.model_dump())


@router.delete("/consents/{consent_id}", response_model=VoiceConsentView)
def revoke_consent(consent_id: str) -> dict:
    return voice_consents.revoke(consent_id)
