"""FastAPI entry point for the local toolkit."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import audio, image, video
from app.services.video import VIDEO_PRESETS
from app.utils.files import MediaError

for media_type in ("audio", "image", "video"):
    (settings.output_dir / media_type).mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="One lightweight local API for audio, image, and video workflows.",
)
app.mount("/outputs", StaticFiles(directory=settings.output_dir), name="outputs")
app.include_router(audio.router)
app.include_router(image.router)
app.include_router(video.router)


@app.exception_handler(FileNotFoundError)
def file_not_found(_: Request, exc: FileNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(MediaError)
def media_error(_: Request, exc: MediaError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.get("/")
def root() -> dict[str, str]:
    return {"name": settings.app_name, "docs": "/docs", "health": "/health"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/capabilities")
def capabilities() -> dict[str, object]:
    return {
        "audio": ["generate", "convert", "normalize", "enhance", "trim", "transcribe"],
        "image": ["generate", "generate-batch", "remove-background", "presets"],
        "video": ["generate", "resize", "frames"],
        "providers": {
            "audio": ["demo", "bark"],
            "image": ["demo"],
            "video": ["demo"],
        },
        "video_presets": VIDEO_PRESETS,
    }
