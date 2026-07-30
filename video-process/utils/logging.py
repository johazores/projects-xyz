"""Logging configuration."""

import logging


def configure_logging(level: str) -> None:
    """Configure concise console logging once."""

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(levelname)s: %(message)s",
        force=True,
    )
