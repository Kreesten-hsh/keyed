from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from typing import Literal, Protocol
from uuid import UUID, uuid4

from keyed.core.errors import InvalidAPIKeyError, RateLimitExceededError
from keyed.core.hashing import extract_key_prefix, generate_api_key, verify_api_key
from keyed.core.models import APIKeyRecord, AuthenticatedAPIKey, IssuedAPIKey
from keyed.core.rate_limit import RateLimitDecision, SlidingWindowRateLimiter


class APIKeyRepository(Protocol):
    async def add(self, record: APIKeyRecord) -> APIKeyRecord: ...

    async def get_by_prefix(self, key_prefix: str) -> APIKeyRecord | None: ...

    async def revoke(self, key_id: UUID, tenant_id: UUID, revoked_at: datetime) -> bool: ...

    async def mark_used(self, key_id: UUID, used_at: datetime) -> None: ...


class APIKeyService:
    def __init__(
        self,
        repository: APIKeyRepository,
        limiter: SlidingWindowRateLimiter,
        *,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._repository = repository
        self._limiter = limiter
        self._now = now or (lambda: datetime.now(UTC))

    async def issue_key(
        self,
        *,
        tenant_id: UUID,
        scopes: Sequence[str],
        rate_limit_per_minute: int = 60,
        environment: Literal["live", "test"] = "live",
        expires_at: datetime | None = None,
    ) -> IssuedAPIKey:
        if rate_limit_per_minute <= 0:
            raise ValueError("rate_limit_per_minute must be positive")

        generated = generate_api_key(environment)
        record = APIKeyRecord(
            id=uuid4(),
            tenant_id=tenant_id,
            key_prefix=generated.prefix,
            key_hash=generated.key_hash,
            key_salt=generated.salt,
            scopes=tuple(dict.fromkeys(scope.strip() for scope in scopes if scope.strip())),
            rate_limit_per_minute=rate_limit_per_minute,
            created_at=self._now(),
            expires_at=expires_at,
        )
        stored_record = await self._repository.add(record)
        return IssuedAPIKey(plaintext=generated.plaintext, record=stored_record)

    async def authenticate(
        self,
        plaintext: str,
    ) -> tuple[AuthenticatedAPIKey, RateLimitDecision]:
        key_prefix = extract_key_prefix(plaintext)
        if key_prefix is None:
            raise InvalidAPIKeyError

        record = await self._repository.get_by_prefix(key_prefix)
        now = self._now()
        if (
            record is None
            or record.revoked_at is not None
            or (record.expires_at is not None and record.expires_at <= now)
            or not verify_api_key(
                plaintext,
                salt=record.key_salt,
                expected_hash=record.key_hash,
            )
        ):
            raise InvalidAPIKeyError

        decision = await self._limiter.check_and_increment(
            record.id,
            limit=record.rate_limit_per_minute,
        )
        if not decision.allowed:
            raise RateLimitExceededError(decision)

        await self._repository.mark_used(record.id, now)
        return (
            AuthenticatedAPIKey(
                key_id=record.id,
                tenant_id=record.tenant_id,
                scopes=record.scopes,
                key_prefix=record.key_prefix,
            ),
            decision,
        )

    async def revoke_key(self, key_id: UUID, tenant_id: UUID) -> bool:
        revoked = await self._repository.revoke(key_id, tenant_id, self._now())
        if revoked:
            self._limiter.clear(key_id)
        return revoked
