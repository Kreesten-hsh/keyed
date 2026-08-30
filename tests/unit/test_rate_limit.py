from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest

from keyed.core.rate_limit import SlidingWindowRateLimiter


class FakeClock:
    def __init__(self, now: float = 0.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


async def test_allows_up_to_limit_then_rejects() -> None:
    limiter = SlidingWindowRateLimiter(clock=FakeClock())
    key_id = uuid4()

    first = await limiter.check_and_increment(key_id, limit=2)
    second = await limiter.check_and_increment(key_id, limit=2)
    rejected = await limiter.check_and_increment(key_id, limit=2)

    assert first.allowed and first.remaining == 1
    assert second.allowed and second.remaining == 0
    assert not rejected.allowed
    assert rejected.retry_after == 60


async def test_sliding_window_does_not_reset_at_fixed_minute_boundary() -> None:
    clock = FakeClock(59.8)
    limiter = SlidingWindowRateLimiter(clock=clock)
    key_id = uuid4()

    assert (await limiter.check_and_increment(key_id, limit=2)).allowed
    clock.advance(0.1)
    assert (await limiter.check_and_increment(key_id, limit=2)).allowed
    clock.advance(0.1)

    assert not (await limiter.check_and_increment(key_id, limit=2)).allowed

    clock.advance(59.8)
    assert (await limiter.check_and_increment(key_id, limit=2)).allowed


async def test_limits_are_isolated_per_key() -> None:
    limiter = SlidingWindowRateLimiter(clock=FakeClock())
    first_key = uuid4()
    second_key = uuid4()

    assert (await limiter.check_and_increment(first_key, limit=1)).allowed
    assert not (await limiter.check_and_increment(first_key, limit=1)).allowed
    assert (await limiter.check_and_increment(second_key, limit=1)).allowed


async def test_concurrent_requests_never_over_admit() -> None:
    limiter = SlidingWindowRateLimiter(clock=FakeClock())
    key_id = uuid4()

    decisions = await asyncio.gather(
        *(limiter.check_and_increment(key_id, limit=10) for _ in range(100))
    )

    assert sum(decision.allowed for decision in decisions) == 10


async def test_clear_removes_existing_window() -> None:
    limiter = SlidingWindowRateLimiter(clock=FakeClock())
    key_id = uuid4()

    assert (await limiter.check_and_increment(key_id, limit=1)).allowed
    assert not (await limiter.check_and_increment(key_id, limit=1)).allowed

    limiter.clear(key_id)

    assert (await limiter.check_and_increment(key_id, limit=1)).allowed


async def test_non_positive_limit_is_rejected() -> None:
    limiter = SlidingWindowRateLimiter(clock=FakeClock())

    with pytest.raises(ValueError, match="limit"):
        await limiter.check_and_increment(uuid4(), limit=0)
