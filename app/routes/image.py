from fastapi import APIRouter

from app.models import (
    BatchOutput,
    ImageBackgroundRequest,
    ImageBatchRequest,
    ImageGenerateRequest,
    MediaOutput,
)
from app.services import image

router = APIRouter(prefix="/image", tags=["image"])

router.get("/presets")(image.list_presets)
router.post("/generate", response_model=MediaOutput)(image.generate)
router.post("/generate-batch", response_model=BatchOutput)(image.generate_batch)
router.post("/remove-background", response_model=MediaOutput)(image.remove_background_file)
