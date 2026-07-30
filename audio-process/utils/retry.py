"""Small retry helper for provider operations."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")
logger = logging.getLogger(__name__)


def run_with_retry(
    operation: Callable[[], T],
    retries: int,
    delay_seconds: float,
) -> T:
    """Run an operation and retry failures a limited number of times."""

    for attempt in range(retries + 1):
        try:
            return operation()
        except Exception:
            if attempt >= retries:
                raise
            logger.warning("Attempt %s failed. Retrying...", attempt + 1)
            if delay_seconds:
                time.sleep(delay_seconds)

    raise RuntimeError("Retry loop ended unexpectedly.")
