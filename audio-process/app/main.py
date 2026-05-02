from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.audio_routes import router as audio_router
from app.core.config import get_settings
from app.utils.files import ensure_directory

settings = get_settings()

ensure_directory(settings.upload_dir)
ensure_directory(settings.processed_dir)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="A beginner-friendly Python backend for audio processing and basic AI audio generation.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/processed", StaticFiles(directory=settings.processed_dir), name="processed")
app.include_router(audio_router)


@app.get("/")
def root():
    return {
        "message": "Python AI Audio Studio is running.",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
