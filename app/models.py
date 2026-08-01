"""Request and response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ProjectRequest(BaseModel):
    project: str | None = Field(default=None, max_length=80)


class GenerateRequest(ProjectRequest):
    prompt: str = Field(min_length=1, max_length=4_000)
    provider: str = Field(default="demo", min_length=1, max_length=100)


class ImageGenerateRequest(ProjectRequest):
    prompt: str = Field(min_length=1, max_length=4_000)
    model: str = Field(default="image.sana-1.6b-int4", min_length=1, max_length=120)
    negative_prompt: str | None = Field(default=None, max_length=4_000)
    preset: str | None = Field(default=None, max_length=100)
    count: int = Field(default=1, ge=1, le=8)
    width: int = Field(default=1024, ge=256, le=1536, multiple_of=32)
    height: int = Field(default=576, ge=256, le=1536, multiple_of=32)
    steps: int = Field(default=20, ge=1, le=50)
    guidance: float = Field(default=4.5, ge=1, le=15)
    seed: int | None = Field(default=None, ge=0, le=2_147_483_647)


class ImageBatchRequest(ProjectRequest):
    prompts: list[str] = Field(min_length=1, max_length=100)
    model: str = Field(default="image.sana-1.6b-int4", min_length=1, max_length=120)
    negative_prompt: str | None = Field(default=None, max_length=4_000)
    preset: str | None = Field(default=None, max_length=100)
    width: int = Field(default=1024, ge=256, le=1536, multiple_of=32)
    height: int = Field(default=576, ge=256, le=1536, multiple_of=32)
    steps: int = Field(default=20, ge=1, le=50)
    guidance: float = Field(default=4.5, ge=1, le=15)
    seed: int | None = Field(default=None, ge=0, le=2_147_483_647)


class LocalFileRequest(ProjectRequest):
    input_path: str = Field(min_length=1, max_length=4_000)


class AudioTrimRequest(LocalFileRequest):
    start: float = Field(default=0, ge=0)
    duration: float = Field(gt=0)


class AudioTranscribeRequest(LocalFileRequest):
    output_format: Literal["txt", "srt"] = "srt"
    language: str | None = Field(default=None, max_length=20)
    model: str | None = Field(default=None, max_length=100)
    device: Literal["auto", "cpu", "cuda"] | None = None
    compute_type: str | None = Field(default=None, max_length=50)


class ImageBackgroundRequest(LocalFileRequest):
    model: str = Field(default="image.birefnet-lite", min_length=1, max_length=120)


class VideoGenerateRequest(ProjectRequest):
    prompt: str = Field(min_length=1, max_length=4_000)
    model: str = Field(default="video.ltx-q8", min_length=1, max_length=120)
    negative_prompt: str = Field(
        default="worst quality, inconsistent motion, blurry, jittery, distorted, watermark, text",
        max_length=4_000,
    )
    input_path: str | None = Field(default=None, max_length=4_000)
    width: int = Field(default=576, ge=256, le=768, multiple_of=32)
    height: int = Field(default=320, ge=256, le=768, multiple_of=32)
    num_frames: int = Field(default=65, ge=9, le=121)
    steps: int = Field(default=20, ge=4, le=50)
    fps: int = Field(default=24, ge=8, le=30)
    seed: int = Field(default=42, ge=0, le=2_147_483_647)
    allow_low_vram_retry: bool = True


class VideoResizeRequest(LocalFileRequest):
    preset: Literal["youtube", "shorts", "square", "720p"] = "youtube"


class VideoFramesRequest(LocalFileRequest):
    fps: float = Field(default=1.0, gt=0, le=60)


class MediaOutput(BaseModel):
    media_type: Literal["audio", "image", "video"]
    operation: str
    provider: str | None = None
    filename: str
    output_path: str
    output_url: str


class BatchOutput(BaseModel):
    items: list[MediaOutput]


JobStatus = Literal["queued", "running", "completed", "failed", "cancelled"]
JobKind = Literal["model", "workflow"]


class JobCreate(BaseModel):
    kind: JobKind
    target: str = Field(min_length=1, max_length=120)
    payload: dict[str, Any] = Field(default_factory=dict)


class JobView(BaseModel):
    id: str
    kind: JobKind
    target: str
    status: JobStatus
    progress: int = Field(ge=0, le=100)
    message: str | None = None
    payload: dict[str, Any]
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    cancel_requested: bool = False


class ModelView(BaseModel):
    id: str
    capability: str
    description: str
    implemented: bool
    recommended: bool
    available: bool
    active: bool
    vram_gb: float | None = None
    dependency_group: str | None = None
    notes: str | None = None


class WorkflowView(BaseModel):
    id: str
    description: str
    implemented: bool
    steps: list[str]


class ThumbnailWorkflowRequest(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    prompt: str = Field(min_length=1, max_length=4_000)
    project: str | None = Field(default=None, max_length=80)
    model: str = Field(default="image.sana-1.6b-int4", max_length=120)
    count: int = Field(default=4, ge=1, le=8)
    width: int = Field(default=1024, ge=512, le=1536, multiple_of=32)
    height: int = Field(default=576, ge=320, le=1024, multiple_of=32)
    steps: int = Field(default=20, ge=1, le=50)
    guidance: float = Field(default=4.5, ge=1, le=15)
    seed: int | None = Field(default=None, ge=0, le=2_147_483_647)
    negative_prompt: str = Field(default="blurry, low quality, watermark, text, logo", max_length=4_000)
    vision_model: str | None = Field(default="vision.florence-2-large", max_length=120)
    subject_path: str | None = Field(default=None, max_length=4_000)
    background_model: str = Field(default="image.birefnet-lite", max_length=120)
    upscale_model: str | None = Field(default="image.realesrgan-ncnn", max_length=120)
    final_width: int = Field(default=1280, ge=640, le=3840)
    final_height: int = Field(default=720, ge=360, le=2160)
    text_position: Literal["auto", "left", "right", "top", "bottom"] = "auto"
    font_path: str | None = Field(default=None, max_length=4_000)
    text_color: str = Field(default="#FFFFFF", pattern=r"^#[0-9A-Fa-f]{6}$")
    accent_color: str = Field(default="#FFD400", pattern=r"^#[0-9A-Fa-f]{6}$")


class ShortScene(BaseModel):
    prompt: str = Field(min_length=1, max_length=2_000)
    text: str | None = Field(default=None, max_length=2_000)
    image_path: str | None = Field(default=None, max_length=4_000)
    duration: float | None = Field(default=None, ge=1, le=20)
    animate: bool = True
    sfx_prompt: str | None = Field(default=None, max_length=1_000)
    sfx_volume: float = Field(default=0.35, ge=0, le=2)


class AiShortWorkflowRequest(BaseModel):
    script: str = Field(min_length=1, max_length=12_000)
    scenes: list[ShortScene] = Field(min_length=1, max_length=12)
    project: str | None = Field(default=None, max_length=80)
    narration_model: str = Field(default="speech.kokoro", max_length=120)
    voice: str = Field(default="af_heart", max_length=120)
    narration_language: str = Field(default="en", max_length=20)
    narration_reference_path: str | None = Field(default=None, max_length=4_000)
    narration_consent_id: str | None = Field(default=None, max_length=120)
    narration_exaggeration: float | None = Field(default=None, ge=0, le=2)
    narration_cfg_weight: float | None = Field(default=None, ge=0, le=2)
    image_model: str = Field(default="image.sana-1.6b-int4", max_length=120)
    video_model: str = Field(default="video.ltx-q8", max_length=120)
    transcription_model: str | None = Field(default="speech.faster-whisper", max_length=120)
    use_motion: bool = True
    fallback_to_stills: bool = True
    image_width: int = Field(default=576, ge=512, le=1024, multiple_of=32)
    image_height: int = Field(default=1024, ge=512, le=1024, multiple_of=32)
    video_width: int = Field(default=320, ge=256, le=768, multiple_of=32)
    video_height: int = Field(default=576, ge=256, le=768, multiple_of=32)
    video_frames: int = Field(default=65, ge=9, le=121)
    video_steps: int = Field(default=20, ge=4, le=50)
    final_width: int = Field(default=1080, ge=540, le=2160)
    final_height: int = Field(default=1920, ge=960, le=3840)
    fps: int = Field(default=30, ge=12, le=60)
    burn_subtitles: bool = False
    music_prompt: str | None = Field(default=None, max_length=2_000)
    music_model: str = Field(default="music.ace-step-1.5", max_length=120)
    music_volume: float = Field(default=0.12, ge=0, le=1)
    sfx_model: str = Field(default="audio.stable-audio-small-sfx", max_length=120)


class MusicGenerateRequest(ProjectRequest):
    prompt: str = Field(min_length=1, max_length=4_000)
    model: str = Field(default="music.ace-step-1.5", max_length=120)
    duration: float = Field(default=30, ge=10, le=600)
    lyrics: str = Field(default="", max_length=12_000)
    instrumental: bool = True
    language: str = Field(default="en", max_length=20)
    bpm: int | None = Field(default=None, ge=30, le=300)
    key_scale: str | None = Field(default=None, max_length=40)
    steps: int = Field(default=8, ge=1, le=20)
    seed: int | None = Field(default=None, ge=0, le=2_147_483_647)


class ExpressiveSpeechRequest(ProjectRequest):
    text: str = Field(min_length=1, max_length=12_000)
    model: str = Field(default="speech.chatterbox-turbo", max_length=120)
    language: str = Field(default="en", max_length=20)
    reference_path: str | None = Field(default=None, max_length=4_000)
    consent_id: str | None = Field(default=None, max_length=120)
    exaggeration: float | None = Field(default=None, ge=0, le=2)
    cfg_weight: float | None = Field(default=None, ge=0, le=2)


class SoundEffectRequest(ProjectRequest):
    prompt: str = Field(min_length=1, max_length=2_000)
    model: str = Field(default="audio.stable-audio-small-sfx", max_length=120)
    duration: float = Field(default=4, ge=0.5, le=120)


class VoiceConsentCreate(BaseModel):
    voice_name: str = Field(min_length=1, max_length=120)
    owner_name: str = Field(min_length=1, max_length=160)
    reference_path: str = Field(min_length=1, max_length=4_000)
    usage_scope: str = Field(min_length=1, max_length=500)
    confirmed: bool
    notes: str | None = Field(default=None, max_length=1_000)


class VoiceConsentView(BaseModel):
    id: str
    voice_name: str
    owner_name: str
    reference_path: str
    reference_sha256: str
    usage_scope: str
    notes: str | None = None
    created_at: datetime
    revoked_at: datetime | None = None


class PodcastSegment(BaseModel):
    speaker: str = Field(min_length=1, max_length=120)
    text: str = Field(min_length=1, max_length=8_000)
    tts_model: str | None = Field(default=None, max_length=120)
    voice: str | None = Field(default=None, max_length=120)
    language: str = Field(default="en", max_length=20)
    reference_path: str | None = Field(default=None, max_length=4_000)
    consent_id: str | None = Field(default=None, max_length=120)
    pause_after: float = Field(default=0.35, ge=0, le=5)


class PodcastWorkflowRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    segments: list[PodcastSegment] = Field(min_length=1, max_length=100)
    project: str | None = Field(default=None, max_length=80)
    narration_model: str = Field(default="speech.kokoro", max_length=120)
    default_voice: str = Field(default="af_heart", max_length=120)
    music_prompt: str | None = Field(default=None, max_length=2_000)
    music_model: str = Field(default="music.ace-step-1.5", max_length=120)
    music_volume: float = Field(default=0.08, ge=0, le=1)
    normalize: bool = True
