"""Keyed API authentication package."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Literal
from uuid import UUID

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from keyed.core.authenticator import SQLAlchemyAPIKeyAuthenticator
from keyed.core.models import IssuedAPIKey
from keyed.core.rate_limit import SlidingWindowRateLimiter
from keyed.core.service import APIKeyService
from keyed.db.repository import SQLAlchemyAPIKeyRepository
from keyed.fastapi import KeyedAuth


class Keyed:
    def __init__(
        self,
        database_url: str | None = None,
        *,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
    ) -> None:
        if database_url is None and session_factory is None:
            raise ValueError("Provide exactly one of database_url or session_factory")
        if database_url is not None and session_factory is not None:
            raise ValueError("Provide exactly one of database_url or session_factory")

        self._engine: AsyncEngine | None = None
        if session_factory is None:
            assert database_url is not None
            self._engine = create_async_engine(database_url, pool_pre_ping=True)
            session_factory = async_sessionmaker(self._engine, expire_on_commit=False)

        self._session_factory = session_factory
        self._limiter = SlidingWindowRateLimiter()
        self.auth = KeyedAuth(SQLAlchemyAPIKeyAuthenticator(self._session_factory, self._limiter))

    async def issue_key(
        self,
        *,
        tenant_id: UUID,
        scopes: Sequence[str],
        rate_limit_per_minute: int = 60,
        environment: Literal["live", "test"] = "live",
        expires_at: datetime | None = None,
    ) -> IssuedAPIKey:
        async with self._session_factory() as session:
            service = APIKeyService(SQLAlchemyAPIKeyRepository(session), self._limiter)
            return await service.issue_key(
                tenant_id=tenant_id,
                scopes=scopes,
                rate_limit_per_minute=rate_limit_per_minute,
                environment=environment,
                expires_at=expires_at,
            )

    async def revoke_key(self, key_id: UUID, tenant_id: UUID) -> bool:
        async with self._session_factory() as session:
            service = APIKeyService(SQLAlchemyAPIKeyRepository(session), self._limiter)
            return await service.revoke_key(key_id, tenant_id)

    async def close(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
