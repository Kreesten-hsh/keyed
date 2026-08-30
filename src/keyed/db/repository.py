from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from keyed.core.models import APIKeyRecord
from keyed.db.models import APIKeyModel


class SQLAlchemyAPIKeyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, record: APIKeyRecord) -> APIKeyRecord:
        model = APIKeyModel(
            id=record.id,
            tenant_id=record.tenant_id,
            key_prefix=record.key_prefix,
            key_hash=record.key_hash,
            key_salt=record.key_salt,
            scopes=list(record.scopes),
            rate_limit_per_minute=record.rate_limit_per_minute,
            created_at=record.created_at,
            expires_at=record.expires_at,
            revoked_at=record.revoked_at,
            last_used_at=record.last_used_at,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_record(model)

    async def get_by_prefix(self, key_prefix: str) -> APIKeyRecord | None:
        result = await self._session.execute(
            select(APIKeyModel).where(APIKeyModel.key_prefix == key_prefix)
        )
        model = result.scalar_one_or_none()
        return None if model is None else _to_record(model)

    async def revoke(self, key_id: UUID, tenant_id: UUID, revoked_at: datetime) -> bool:
        result = await self._session.execute(
            update(APIKeyModel)
            .where(
                APIKeyModel.id == key_id,
                APIKeyModel.tenant_id == tenant_id,
                APIKeyModel.revoked_at.is_(None),
            )
            .values(revoked_at=revoked_at)
            .returning(APIKeyModel.id)
        )
        await self._session.commit()
        return result.scalar_one_or_none() is not None

    async def mark_used(self, key_id: UUID, used_at: datetime) -> None:
        await self._session.execute(
            update(APIKeyModel).where(APIKeyModel.id == key_id).values(last_used_at=used_at)
        )
        await self._session.commit()


def _to_record(model: APIKeyModel) -> APIKeyRecord:
    return APIKeyRecord(
        id=model.id,
        tenant_id=model.tenant_id,
        key_prefix=model.key_prefix,
        key_hash=model.key_hash,
        key_salt=model.key_salt,
        scopes=tuple(model.scopes),
        rate_limit_per_minute=model.rate_limit_per_minute,
        created_at=model.created_at,
        expires_at=model.expires_at,
        revoked_at=model.revoked_at,
        last_used_at=model.last_used_at,
    )
