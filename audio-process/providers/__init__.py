"""Audio provider selection."""

from __future__ import annotations

from providers.base import AudioProvider
from providers.demo import DemoAudioProvider


def get_provider(name: str) -> AudioProvider:
    """Return a configured provider by its short name."""

    normalized = name.strip().lower()
    if normalized == "demo":
        return DemoAudioProvider()
    if normalized == "bark":
        from providers.bark import BarkAudioProvider

        return BarkAudioProvider()

    raise ValueError(f"Unknown audio provider: {name}. Available providers: demo, bark.")
