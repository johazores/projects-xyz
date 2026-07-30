"""Image provider selection."""

from __future__ import annotations

from providers.base import ImageProvider
from providers.demo import DemoImageProvider


def get_provider(name: str) -> ImageProvider:
    """Return an image provider by its short name."""

    normalized = name.strip().lower()
    if normalized == "demo":
        return DemoImageProvider()

    raise ValueError(f"Unknown image provider: {name}. Available providers: demo.")
