from __future__ import annotations

import asyncio
import math
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.ext.asyncio import AsyncSession

from keyed.db.models import RateLimitCounterModel


@dataclass(frozen=True, slots=True)
class RateLimitDecision:
    allowed: bool
    limit: int
    remaining: int
    retry_after: int


class RateLimiter(Protocol):
    async def check_and_increment(
        self,
        key_id: UUID,
        *,
        limit: int,
        window_seconds: int = 60,
        session: AsyncSession | None = None,
    ) -> RateLimitDecision: ...

    def clear(self, key_id: UUID) -> None: ...


class SlidingWindowRateLimiter:
    def __init__(self, *, clock: Callable[[], float] | None = None) -> None:
        self._clock = clock or time.monotonic
        self._events: dict[UUID, deque[float]] = {}
        self._lock = asyncio.Lock()

        # Counters intentionally live only in this process and reset on restart.
        # This implementation is retained for isolated unit tests without PostgreSQL.

    async def check_and_increment(
        self,
        key_id: UUID,
        *,
        limit: int,
        window_seconds: int = 60,
        session: AsyncSession | None = None,
    ) -> RateLimitDecision:
        del session
        _validate_configuration(limit, window_seconds)

        now = self._clock()
        cutoff = now - window_seconds

        async with self._lock:
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
        # The async critical section contains no await, so synchronous teardown cannot
        # interleave with mutation on the same event loop.
        self._events.pop(key_id, None)


class PostgresRateLimiter:
    def __init__(self, *, now: Callable[[], datetime] | None = None) -> None:
        self._now = now or (lambda: datetime.now(UTC))

    async def check_and_increment(
        self,
        key_id: UUID,
        *,
        limit: int,
        window_seconds: int = 60,
        session: AsyncSession | None = None,
    ) -> RateLimitDecision:
        _validate_configuration(limit, window_seconds)
        if session is None:
            raise ValueError("session is required for PostgresRateLimiter")

        now = self._now()
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")
        now_window = _floor_window(now, window_seconds)

        counter = await self._get_for_update(session, key_id)
        if counter is None:
            inserted = await session.scalar(
                postgresql_insert(RateLimitCounterModel)
                .values(
                    key_id=key_id,
                    window_start=now_window,
                    curr_count=1,
                    prev_count=0,
                )
                .on_conflict_do_nothing(index_elements=[RateLimitCounterModel.key_id])
                .returning(RateLimitCounterModel.key_id)
            )
            if inserted is not None:
                await session.commit()
                return RateLimitDecision(True, limit, limit - 1, 0)

            counter = await self._get_for_update(session, key_id)
            if counter is None:
                raise RuntimeError("rate limit counter disappeared after concurrent insert")

        prev_count, curr_count = _counts_for_window(
            counter,
            now_window=now_window,
            window_seconds=window_seconds,
        )
        elapsed = (now - now_window).total_seconds()
        effective = prev_count * (1 - elapsed / window_seconds) + curr_count
        projected = effective + 1

        if projected > limit:
            return RateLimitDecision(
                allowed=False,
                limit=limit,
                remaining=0,
                retry_after=_retry_after(
                    prev_count=prev_count,
                    curr_count=curr_count,
                    elapsed=elapsed,
                    limit=limit,
                    window_seconds=window_seconds,
                ),
            )

        counter.window_start = now_window
        counter.prev_count = prev_count
        counter.curr_count = curr_count + 1
        await session.commit()
        return RateLimitDecision(
            allowed=True,
            limit=limit,
            remaining=max(0, math.floor(limit - projected)),
            retry_after=0,
        )

    def clear(self, key_id: UUID) -> None:
        pass

    @staticmethod
    async def _get_for_update(
        session: AsyncSession,
        key_id: UUID,
    ) -> RateLimitCounterModel | None:
        result = await session.execute(
            select(RateLimitCounterModel)
            .where(RateLimitCounterModel.key_id == key_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()


def _validate_configuration(limit: int, window_seconds: int) -> None:
    if limit <= 0:
        raise ValueError("limit must be positive")
    if window_seconds <= 0:
        raise ValueError("window_seconds must be positive")


def _floor_window(now: datetime, window_seconds: int) -> datetime:
    epoch_seconds = math.floor(now.timestamp() / window_seconds) * window_seconds
    return datetime.fromtimestamp(epoch_seconds, tz=UTC)


def _counts_for_window(
    counter: RateLimitCounterModel,
    *,
    now_window: datetime,
    window_seconds: int,
) -> tuple[int, int]:
    bucket_age = math.floor((now_window - counter.window_start).total_seconds() / window_seconds)
    if bucket_age <= 0:
        return counter.prev_count, counter.curr_count
    if bucket_age == 1:
        return counter.curr_count, 0
    return 0, 0


def _retry_after(
    *,
    prev_count: int,
    curr_count: int,
    elapsed: float,
    limit: int,
    window_seconds: int,
) -> int:
    target_effective = limit - 1
    target_previous = target_effective - curr_count
    if prev_count > 0 and target_previous >= 0:
        required_elapsed = window_seconds * (1 - target_previous / prev_count)
        return max(1, math.ceil(required_elapsed - elapsed))

    next_window_wait = window_seconds - elapsed
    if curr_count == 0:
        return max(1, math.ceil(next_window_wait))

    next_window_elapsed = window_seconds * (1 - target_effective / curr_count)
    return max(1, math.ceil(next_window_wait + max(0, next_window_elapsed)))
