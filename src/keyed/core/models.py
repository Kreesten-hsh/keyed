from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class APIKeyRecord:
    id: UUID
    tenant_id: UUID
    key_prefix: str
    key_hash: bytes
    key_salt: bytes
    scopes: tuple[str, ...]
    rate_limit_per_minute: int
    created_at: datetime
    expires_at: datetime | None = None
    revoked_at: datetime | None = None
    last_used_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class IssuedAPIKey:
    plaintext: str = field(repr=False)
    record: APIKeyRecord


@dataclass(frozen=True, slots=True)
class AuthenticatedAPIKey:
    key_id: UUID
    tenant_id: UUID
    scopes: tuple[str, ...]
    key_prefix: str
