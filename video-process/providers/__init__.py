"""Video provider selection."""

from __future__ import annotations

from providers.base import VideoProvider
from providers.demo import DemoVideoProvider


def get_provider(name: str) -> VideoProvider:
    """Return a video provider by its short name."""

    normalized = name.strip().lower()
    if normalized == "demo":
        return DemoVideoProvider()

    raise ValueError(f"Unknown video provider: {name}. Available providers: demo.")
