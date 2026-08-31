from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from keyed.core.authenticator import SQLAlchemyAPIKeyAuthenticator
from keyed.core.errors import RateLimitExceededError
from keyed.core.rate_limit import PostgresRateLimiter, RateLimitDecision, SlidingWindowRateLimiter
from keyed.core.service import APIKeyService
from keyed.db.base import Base
from keyed.db.models import APIKeyModel, RateLimitCounterModel
from keyed.db.repository import SQLAlchemyAPIKeyRepository

pytestmark = pytest.mark.integration

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")


class MutableClock:
    def __init__(self, now: datetime) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now


@pytest.fixture
async def session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    if TEST_DATABASE_URL is None:
        pytest.skip("TEST_DATABASE_URL is required for PostgreSQL integration tests")
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    yield async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


async def issue_key(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    limit: int = 60,
) -> tuple[str, UUID]:
    async with session_factory() as session:
        service = APIKeyService(
            SQLAlchemyAPIKeyRepository(session),
            SlidingWindowRateLimiter(),
        )
        issued = await service.issue_key(
            tenant_id=uuid4(),
            scopes=[],
            rate_limit_per_minute=limit,
            environment="test",
        )
    return issued.plaintext, issued.record.id


async def check_once(
    session_factory: async_sessionmaker[AsyncSession],
    limiter: PostgresRateLimiter,
    key_id: UUID,
    *,
    limit: int,
) -> RateLimitDecision:
    async with session_factory() as session:
        return await limiter.check_and_increment(
            key_id,
            limit=limit,
            session=session,
        )


async def test_postgres_limiter_requires_callers_open_session() -> None:
    with pytest.raises(ValueError, match="session"):
        await PostgresRateLimiter().check_and_increment(uuid4(), limit=1)


async def test_first_request_inserts_single_counter_row(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    _, key_id = await issue_key(session_factory)

    decision = await check_once(session_factory, PostgresRateLimiter(), key_id, limit=60)

    assert decision == RateLimitDecision(True, 60, 59, 0)
    async with session_factory() as session:
        counter = await session.get(RateLimitCounterModel, key_id)
        row_count = await session.scalar(select(func.count()).select_from(RateLimitCounterModel))
    assert counter is not None
    assert counter.curr_count == 1
    assert counter.prev_count == 0
    assert row_count == 1


async def test_exact_window_boundary_shifts_current_bucket(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    _, key_id = await issue_key(session_factory)
    start = datetime(2026, 8, 31, 12, 0, tzinfo=UTC)
    clock = MutableClock(start)
    limiter = PostgresRateLimiter(now=clock)

    assert (await check_once(session_factory, limiter, key_id, limit=4)).allowed
    clock.now = start + timedelta(seconds=59, milliseconds=999)
    assert (await check_once(session_factory, limiter, key_id, limit=4)).allowed
    clock.now = start + timedelta(seconds=60)
    assert (await check_once(session_factory, limiter, key_id, limit=4)).allowed

    async with session_factory() as session:
        counter = await session.get(RateLimitCounterModel, key_id)
    assert counter is not None
    assert counter.window_start == start + timedelta(seconds=60)
    assert counter.prev_count == 2
    assert counter.curr_count == 1


async def test_burst_of_limit_requests_is_fully_allowed(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    _, key_id = await issue_key(session_factory)
    limiter = PostgresRateLimiter(now=lambda: datetime(2026, 8, 31, 12, 0, 1, tzinfo=UTC))

    decisions = await asyncio.gather(
        *(check_once(session_factory, limiter, key_id, limit=60) for _ in range(60))
    )
    rejected = await check_once(session_factory, limiter, key_id, limit=60)

    assert sum(decision.allowed for decision in decisions) == 60
    assert not rejected.allowed
    async with session_factory() as session:
        counter = await session.get(RateLimitCounterModel, key_id)
    assert counter is not None
    assert counter.curr_count == 60


async def test_limit_one_allows_exactly_one_request_per_window(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    _, key_id = await issue_key(session_factory, limit=1)
    clock = MutableClock(datetime(2026, 8, 31, 12, 0, tzinfo=UTC))
    limiter = PostgresRateLimiter(now=clock)

    assert (await check_once(session_factory, limiter, key_id, limit=1)).allowed
    assert not (await check_once(session_factory, limiter, key_id, limit=1)).allowed
    clock.now += timedelta(seconds=120)
    assert (await check_once(session_factory, limiter, key_id, limit=1)).allowed


async def test_authenticator_restart_preserves_previous_count(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    plaintext, _ = await issue_key(session_factory, limit=1)

    first_authenticator = SQLAlchemyAPIKeyAuthenticator(session_factory)
    _, first = await first_authenticator.authenticate(plaintext)
    restarted_authenticator = SQLAlchemyAPIKeyAuthenticator(session_factory)

    assert first.allowed
    with pytest.raises(RateLimitExceededError):
        await restarted_authenticator.authenticate(plaintext)


async def test_deleting_key_cascades_to_counter_row(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    _, key_id = await issue_key(session_factory)
    await check_once(session_factory, PostgresRateLimiter(), key_id, limit=60)

    async with session_factory() as session:
        await session.execute(delete(APIKeyModel).where(APIKeyModel.id == key_id))
        await session.commit()

    async with session_factory() as session:
        assert await session.get(RateLimitCounterModel, key_id) is None
