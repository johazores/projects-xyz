from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Python AI Audio Studio"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    base_url: str = "http://localhost:8000"

    upload_dir: str = "uploads"
    processed_dir: str = "processed"

    ai_model_name: str = "suno/bark-small"
    ai_device: str = "auto"  # auto, cpu, cuda

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
