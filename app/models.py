"""Request and response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ProjectRequest(BaseModel):
    project: str | None = Field(default=None, max_length=80)


class GenerateRequest(ProjectRequest):
    prompt: str = Field(min_length=1, max_length=4_000)
    provider: str = Field(default="demo", min_length=1, max_length=100)


class ImageGenerateRequest(GenerateRequest):
    negative_prompt: str | None = Field(default=None, max_length=4_000)
    preset: str | None = Field(default=None, max_length=100)


class ImageBatchRequest(ProjectRequest):
    prompts: list[str] = Field(min_length=1, max_length=100)
    provider: str = Field(default="demo", min_length=1, max_length=100)
    negative_prompt: str | None = Field(default=None, max_length=4_000)
    preset: str | None = Field(default=None, max_length=100)


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
    model: str = Field(default="u2net", min_length=1, max_length=100)


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
