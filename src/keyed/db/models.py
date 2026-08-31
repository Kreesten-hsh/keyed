from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, LargeBinary, String, func, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from keyed.db.base import Base


class APIKeyModel(Base):
    __tablename__ = "api_keys"
    __table_args__ = (
        CheckConstraint("rate_limit_per_minute > 0", name="ck_api_keys_positive_rate_limit"),
    )

    id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    key_prefix: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    key_hash: Mapped[bytes] = mapped_column(LargeBinary(32), nullable=False)
    key_salt: Mapped[bytes] = mapped_column(LargeBinary(32), nullable=False)
    scopes: Mapped[list[str]] = mapped_column(
        ARRAY(String(128)),
        nullable=False,
        default=list,
        server_default=text("'{}'::varchar[]"),
    )
    rate_limit_per_minute: Mapped[int] = mapped_column(
        nullable=False,
        default=60,
        server_default=text("60"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class RateLimitCounterModel(Base):
    __tablename__ = "rate_limit_counters"

    key_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("api_keys.id", ondelete="CASCADE"),
        primary_key=True,
    )
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    curr_count: Mapped[int] = mapped_column(nullable=False, default=0, server_default=text("0"))
    prev_count: Mapped[int] = mapped_column(nullable=False, default=0, server_default=text("0"))
