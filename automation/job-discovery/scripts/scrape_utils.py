"""
Scraper utilities: rate limiting and retry wrappers.
"""
from __future__ import annotations

import time
import random
import logging
from typing import Callable, TypeVar, Optional, Tuple

T = TypeVar("T")
logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple per-minute rate limiter.

    - rpm: allowed calls per minute
    - now_fn: injectable time function for tests
    - sleep_fn: injectable sleep function for tests
    """

    def __init__(self, rpm: int = 60, now_fn: Callable[[], float] = time.time, sleep_fn: Callable[[float], None] = time.sleep):
        self.rpm = max(1, int(rpm))
        self._now = now_fn
        self._sleep = sleep_fn
        self._window_start = self._now()
        self._count = 0

    def acquire(self) -> None:
        now = self._now()
        elapsed = now - self._window_start
        if elapsed >= 60.0:
            # reset window
            self._window_start = now
            self._count = 0
        if self._count >= self.rpm:
            wait = max(0.0, 60.0 - elapsed)
            if wait > 0:
                logger.info("rate limit reached; sleeping %.2fs", wait)
                self._sleep(wait)
            # reset after waiting
            self._window_start = self._now()
            self._count = 0
        self._count += 1


def with_retry(
    func: Callable[[], T],
    max_retries: int = 3,
    backoff_base: float = 0.5,
    backoff_max: float = 5.0,
    jitter_ms: int = 100,
    sleep_fn: Callable[[float], None] = time.sleep,
    on_error: Optional[Callable[[int, BaseException], None]] = None,
) -> Optional[T]:
    """Execute func with exponential backoff + jitter on exceptions.

    Returns the function result, or None after exhausting retries.
    Logs structured messages on failures.
    """
    attempts = 0
    while True:
        try:
            return func()
        except BaseException as e:  # noqa: BLE001
            attempts += 1
            if on_error:
                on_error(attempts, e)
            logger.error("scraper attempt %d failed: %s", attempts, e, exc_info=True)
            if attempts > max_retries:
                logger.error("scraper exhausted retries (max=%d)", max_retries)
                return None
            # compute backoff with jitter
            delay = min(backoff_max, backoff_base * (2 ** (attempts - 1)))
            delay += random.uniform(0, jitter_ms / 1000.0)
            sleep_fn(delay)

