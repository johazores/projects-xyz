"""FastAPI entry point for the local media processing toolkit."""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import PROVIDER_CATALOG, settings
from app.routes import audio, image, video
from app.services.runner import ProcessExecutionError

settings.output_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="A lightweight local API for the repository audio, image, and video tools.",
)
app.mount("/outputs", StaticFiles(directory=settings.output_dir), name="outputs")
app.include_router(audio.router)
app.include_router(image.router)
app.include_router(video.router)


@app.exception_handler(ProcessExecutionError)
def process_error_handler(_: Request, exc: ProcessExecutionError) -> JSONResponse:
    """Return a consistent error when a media process fails."""

    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.get("/")
def root() -> dict[str, str]:
    """Return basic navigation for local development."""

    return {
        "message": settings.app_name,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health() -> dict[str, str]:
    """Confirm the API process is running."""

    return {"status": "ok"}


@app.get("/providers")
def providers() -> dict[str, list[str]]:
    """List providers currently exposed by each media project."""

    return {
        media_type: list(provider_models)
        for media_type, provider_models in PROVIDER_CATALOG.items()
    }


@app.get("/models")
def models() -> dict[str, dict[str, list[str]]]:
    """List the known model or demo implementation for each provider."""

    return PROVIDER_CATALOG
