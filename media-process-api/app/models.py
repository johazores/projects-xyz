"""Request and response models shared by the routes."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Common generation request fields."""

    prompt: str = Field(min_length=1, max_length=4_000)
    provider: str = Field(default="demo", min_length=1, max_length=100)


class ImageGenerateRequest(GenerateRequest):
    """Image generation request with an optional negative prompt."""

    negative_prompt: str | None = Field(default=None, max_length=4_000)


class MediaOutput(BaseModel):
    """Metadata returned after a media artifact is created."""

    media_type: Literal["audio", "image", "video"]
    provider: str
    filename: str
    output_path: str
    output_url: str
