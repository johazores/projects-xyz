from pathlib import Path
from uuid import uuid4
import shutil
from fastapi import UploadFile


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def safe_file_extension(filename: str, fallback: str = ".bin") -> str:
    suffix = Path(filename or "").suffix.lower()
    return suffix if suffix else fallback


def unique_filename(prefix: str, extension: str) -> str:
    extension = extension if extension.startswith(".") else f".{extension}"
    return f"{prefix}-{uuid4().hex}{extension}"


def save_upload_file(upload_file: UploadFile, destination: Path) -> None:
    with destination.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)


def remove_file_if_exists(path: str | Path) -> None:
    file_path = Path(path)
    if file_path.exists() and file_path.is_file():
        file_path.unlink()
