"""FastAPI entry point for the local AI content studio."""

from __future__ import annotations

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import audio, image, jobs, models as model_routes, video, workflows
from app.runtime.state import models, registry, worker
from app.services.video import VIDEO_PRESETS
from app.utils.files import MediaError

for directory in (settings.output_dir, settings.data_dir):
    directory.mkdir(parents=True, exist_ok=True)
for media_type in ("audio", "image", "video", "workflow"):
    (settings.output_dir / media_type).mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    worker.start()
    yield
    worker.stop()


app = FastAPI(
    title=settings.app_name,
    version="1.1.0",
    description="Local-first AI content creation studio with a serialized GPU job queue.",
    lifespan=lifespan,
)
app.mount("/outputs", StaticFiles(directory=settings.output_dir), name="outputs")
for router in (audio.router, image.router, video.router, jobs.router, model_routes.router, workflows.router):
    app.include_router(router)


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
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "worker_running": worker.running,
        "queued_jobs": worker.queue.qsize(),
        "active_model": models.active_id,
    }


@app.get("/capabilities")
def capabilities() -> dict[str, object]:
    return {
        "audio": ["generate", "convert", "normalize", "enhance", "trim", "transcribe"],
        "image": ["generate", "generate-batch", "remove-background", "presets"],
        "video": ["generate", "resize", "frames"],
        "jobs": ["submit", "status", "list", "cancel"],
        "models": [spec.id for spec in registry.list() if spec.implemented],
        "planned_models": [spec.id for spec in registry.list() if not spec.implemented],
        "workflows": ["youtube.narration", "youtube.social-clip-prep"],
        "video_presets": VIDEO_PRESETS,
    }
