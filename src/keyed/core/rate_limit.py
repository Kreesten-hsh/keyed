from __future__ import annotations

import math
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from threading import Lock
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RateLimitDecision:
    allowed: bool
    limit: int
    remaining: int
    retry_after: int


class SlidingWindowRateLimiter:
    def __init__(self, *, clock: Callable[[], float] | None = None) -> None:
        self._clock = clock or time.monotonic
        self._events: dict[UUID, deque[float]] = {}
        self._lock = Lock()

        # Counters intentionally live only in this process and reset on restart.
        # This keeps the default deployment free of Redis or another paid service.

    async def check_and_increment(
        self,
        key_id: UUID,
        *,
        limit: int,
        window_seconds: int = 60,
    ) -> RateLimitDecision:
        if limit <= 0:
            raise ValueError("limit must be positive")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")

        now = self._clock()
        cutoff = now - window_seconds

        with self._lock:
            events = self._events.setdefault(key_id, deque())
            while events and events[0] <= cutoff:
                events.popleft()

            if len(events) >= limit:
                retry_after = max(1, math.ceil(events[0] + window_seconds - now))
                return RateLimitDecision(
                    allowed=False,
                    limit=limit,
                    remaining=0,
                    retry_after=retry_after,
                )

            events.append(now)
            return RateLimitDecision(
                allowed=True,
                limit=limit,
                remaining=limit - len(events),
                retry_after=0,
            )

    def clear(self, key_id: UUID) -> None:
        with self._lock:
            self._events.pop(key_id, None)
