from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from keyed.core.errors import InvalidAPIKeyError, RateLimitExceededError
from keyed.core.models import APIKeyRecord
from keyed.core.rate_limit import RateLimitDecision, SlidingWindowRateLimiter
from keyed.core.scopes import has_required_scopes
from keyed.core.service import APIKeyService


class InMemoryAPIKeyRepository:
    def __init__(self) -> None:
        self.records: dict[UUID, APIKeyRecord] = {}

    async def add(self, record: APIKeyRecord) -> APIKeyRecord:
        self.records[record.id] = record
        return record

    async def get_by_prefix(self, key_prefix: str) -> APIKeyRecord | None:
        return next(
            (record for record in self.records.values() if record.key_prefix == key_prefix),
            None,
        )

    async def revoke(self, key_id: UUID, tenant_id: UUID, revoked_at: datetime) -> bool:
        record = self.records.get(key_id)
        if record is None or record.tenant_id != tenant_id:
            return False
        self.records[key_id] = replace(record, revoked_at=revoked_at)
        return True

    async def mark_used(self, key_id: UUID, used_at: datetime) -> None:
        self.records[key_id] = replace(self.records[key_id], last_used_at=used_at)


class RecordingRateLimiter:
    def __init__(self) -> None:
        self.session: AsyncSession | None = None

    async def check_and_increment(
        self,
        key_id: UUID,
        *,
        limit: int,
        window_seconds: int = 60,
        session: AsyncSession | None = None,
    ) -> RateLimitDecision:
        self.session = session
        return RateLimitDecision(True, limit, limit - 1, 0)

    def clear(self, key_id: UUID) -> None:
        return None


@pytest.fixture
def now() -> datetime:
    return datetime(2026, 8, 30, 12, 0, tzinfo=UTC)


@pytest.fixture
def repository() -> InMemoryAPIKeyRepository:
    return InMemoryAPIKeyRepository()


@pytest.fixture
def service(
    repository: InMemoryAPIKeyRepository,
    now: datetime,
) -> APIKeyService:
    return APIKeyService(
        repository,
        SlidingWindowRateLimiter(),
        now=lambda: now,
    )


async def test_issue_key_persists_only_hash_material(
    service: APIKeyService,
    repository: InMemoryAPIKeyRepository,
) -> None:
    tenant_id = uuid4()

    issued = await service.issue_key(
        tenant_id=tenant_id,
        scopes=["documents:read", "documents:read"],
        rate_limit_per_minute=10,
        environment="test",
    )

    stored = repository.records[issued.record.id]
    assert issued.plaintext.startswith(stored.key_prefix)
    assert issued.plaintext not in repr(issued)
    assert stored.scopes == ("documents:read",)
    assert not hasattr(stored, "plaintext")


async def test_valid_key_authenticates_and_updates_last_used(
    service: APIKeyService,
    repository: InMemoryAPIKeyRepository,
    now: datetime,
) -> None:
    issued = await service.issue_key(
        tenant_id=uuid4(),
        scopes=["documents:read"],
        rate_limit_per_minute=10,
    )

    principal, decision = await service.authenticate(issued.plaintext)

    assert principal.key_id == issued.record.id
    assert principal.scopes == ("documents:read",)
    assert decision.allowed
    assert repository.records[issued.record.id].last_used_at == now


async def test_invalid_key_is_rejected(service: APIKeyService) -> None:
    with pytest.raises(InvalidAPIKeyError):
        await service.authenticate("not-a-key")


async def test_rate_limit_is_applied_per_key(service: APIKeyService) -> None:
    issued = await service.issue_key(
        tenant_id=uuid4(),
        scopes=[],
        rate_limit_per_minute=1,
    )

    await service.authenticate(issued.plaintext)

    with pytest.raises(RateLimitExceededError):
        await service.authenticate(issued.plaintext)


async def test_authentication_passes_open_session_to_rate_limiter(
    repository: InMemoryAPIKeyRepository,
    now: datetime,
) -> None:
    limiter = RecordingRateLimiter()
    async with AsyncSession() as session:
        service = APIKeyService(repository, limiter, session=session, now=lambda: now)
        issued = await service.issue_key(tenant_id=uuid4(), scopes=[])

        await service.authenticate(issued.plaintext)

        assert limiter.session is session


async def test_issue_key_rejects_non_positive_rate_limit(service: APIKeyService) -> None:
    with pytest.raises(ValueError, match="rate_limit_per_minute"):
        await service.issue_key(
            tenant_id=uuid4(),
            scopes=[],
            rate_limit_per_minute=0,
        )


async def test_revoked_key_is_rejected_even_when_hash_is_correct(
    service: APIKeyService,
    repository: InMemoryAPIKeyRepository,
    now: datetime,
) -> None:
    issued = await service.issue_key(tenant_id=uuid4(), scopes=[])
    repository.records[issued.record.id] = replace(issued.record, revoked_at=now)

    with pytest.raises(InvalidAPIKeyError):
        await service.authenticate(issued.plaintext)


async def test_revoke_key_is_scoped_to_tenant(
    service: APIKeyService,
    repository: InMemoryAPIKeyRepository,
) -> None:
    tenant_id = uuid4()
    issued = await service.issue_key(tenant_id=tenant_id, scopes=[])

    assert not await service.revoke_key(issued.record.id, uuid4())
    assert repository.records[issued.record.id].revoked_at is None
    assert await service.revoke_key(issued.record.id, tenant_id)
    assert repository.records[issued.record.id].revoked_at is not None


async def test_expired_key_is_rejected(
    service: APIKeyService,
    repository: InMemoryAPIKeyRepository,
    now: datetime,
) -> None:
    issued = await service.issue_key(tenant_id=uuid4(), scopes=[])
    repository.records[issued.record.id] = replace(
        issued.record,
        expires_at=now - timedelta(seconds=1),
    )

    with pytest.raises(InvalidAPIKeyError):
        await service.authenticate(issued.plaintext)


def test_scope_check_requires_every_requested_scope() -> None:
    assert has_required_scopes(("documents:read", "documents:write"), ("documents:read",))
    assert not has_required_scopes(("documents:read",), ("documents:write",))
    assert not has_required_scopes(("documents:read",), ("documents:*",))
