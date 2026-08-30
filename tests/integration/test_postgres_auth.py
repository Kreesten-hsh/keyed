from __future__ import annotations

import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from keyed import Keyed
from keyed.core.authenticator import SQLAlchemyAPIKeyAuthenticator
from keyed.core.models import AuthenticatedAPIKey
from keyed.core.rate_limit import SlidingWindowRateLimiter
from keyed.core.service import APIKeyService
from keyed.db.base import Base
from keyed.db.repository import SQLAlchemyAPIKeyRepository
from keyed.fastapi import KeyedAuth

pytestmark = pytest.mark.integration

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")


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


def create_protected_app(authenticator: SQLAlchemyAPIKeyAuthenticator) -> FastAPI:
    app = FastAPI()
    auth = KeyedAuth(authenticator)

    @app.get("/protected")
    async def protected(
        principal: AuthenticatedAPIKey = Depends(auth.require_scopes("documents:read")),
    ) -> dict[str, str]:
        return {"key_id": str(principal.key_id)}

    return app


async def test_create_call_revoke_cycle(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    limiter = SlidingWindowRateLimiter()
    tenant_id = uuid4()

    async with session_factory() as session:
        service = APIKeyService(SQLAlchemyAPIKeyRepository(session), limiter)
        issued = await service.issue_key(
            tenant_id=tenant_id,
            scopes=["documents:read"],
            rate_limit_per_minute=10,
            environment="test",
        )

    app = create_protected_app(SQLAlchemyAPIKeyAuthenticator(session_factory, limiter))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        accepted = await client.get(
            "/protected",
            headers={"X-API-Key": issued.plaintext},
        )

        async with session_factory() as session:
            service = APIKeyService(SQLAlchemyAPIKeyRepository(session), limiter)
            assert await service.revoke_key(issued.record.id, tenant_id)

        rejected = await client.get(
            "/protected",
            headers={"X-API-Key": issued.plaintext},
        )

    assert accepted.status_code == 200
    assert rejected.status_code == 401

    async with session_factory() as session:
        stored = await SQLAlchemyAPIKeyRepository(session).get_by_prefix(issued.record.key_prefix)
    assert stored is not None
    assert stored.last_used_at is not None
    assert stored.revoked_at is not None


async def test_expired_key_is_refused(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    limiter = SlidingWindowRateLimiter()
    async with session_factory() as session:
        service = APIKeyService(SQLAlchemyAPIKeyRepository(session), limiter)
        issued = await service.issue_key(
            tenant_id=uuid4(),
            scopes=["documents:read"],
            expires_at=datetime.now(UTC) - timedelta(seconds=1),
            environment="test",
        )

    app = create_protected_app(SQLAlchemyAPIKeyAuthenticator(session_factory, limiter))
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/protected",
            headers={"X-API-Key": issued.plaintext},
        )

    assert response.status_code == 401


async def test_keyed_facade_is_the_single_fastapi_integration_point(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    runtime = Keyed(session_factory=session_factory)
    tenant_id = uuid4()
    issued = await runtime.issue_key(
        tenant_id=tenant_id,
        scopes=["documents:read"],
        environment="test",
    )
    app = FastAPI()

    @app.get("/documents")
    async def documents(
        principal: AuthenticatedAPIKey = Depends(runtime.auth.require_scopes("documents:read")),
    ) -> dict[str, str]:
        return {"tenant_id": str(principal.tenant_id)}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        accepted = await client.get(
            "/documents",
            headers={"X-API-Key": issued.plaintext},
        )
        assert await runtime.revoke_key(issued.record.id, tenant_id)
        revoked = await client.get(
            "/documents",
            headers={"X-API-Key": issued.plaintext},
        )

    assert accepted.status_code == 200
    assert revoked.status_code == 401
