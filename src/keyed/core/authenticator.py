from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from keyed.core.models import AuthenticatedAPIKey
from keyed.core.rate_limit import RateLimitDecision, SlidingWindowRateLimiter
from keyed.core.service import APIKeyService
from keyed.db.repository import SQLAlchemyAPIKeyRepository


class SQLAlchemyAPIKeyAuthenticator:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        limiter: SlidingWindowRateLimiter | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._limiter = limiter or SlidingWindowRateLimiter()

    async def authenticate(
        self,
        plaintext: str,
    ) -> tuple[AuthenticatedAPIKey, RateLimitDecision]:
        async with self._session_factory() as session:
            service = APIKeyService(SQLAlchemyAPIKeyRepository(session), self._limiter)
            return await service.authenticate(plaintext)
