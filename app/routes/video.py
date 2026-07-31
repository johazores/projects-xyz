from fastapi import APIRouter

from app.models import GenerateRequest, MediaOutput, VideoFramesRequest, VideoResizeRequest
from app.services import video

router = APIRouter(prefix="/video", tags=["video"])

router.post("/generate", response_model=MediaOutput)(video.generate)
router.post("/resize", response_model=MediaOutput)(video.resize)
router.post("/frames", response_model=MediaOutput)(video.frames)
