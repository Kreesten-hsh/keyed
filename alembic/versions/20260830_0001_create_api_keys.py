"""Create API key storage.

Revision ID: 20260830_0001
Revises:
Create Date: 2026-08-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260830_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("key_prefix", sa.String(length=128), nullable=False),
        sa.Column("key_hash", sa.LargeBinary(length=32), nullable=False),
        sa.Column("key_salt", sa.LargeBinary(length=32), nullable=False),
        sa.Column(
            "scopes",
            postgresql.ARRAY(sa.String(length=128)),
            server_default=sa.text("'{}'::varchar[]"),
            nullable=False,
        ),
        sa.Column(
            "rate_limit_per_minute",
            sa.Integer(),
            server_default=sa.text("60"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "rate_limit_per_minute > 0",
            name="ck_api_keys_positive_rate_limit",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_api_keys"),
        sa.UniqueConstraint("key_prefix", name="uq_api_keys_key_prefix"),
    )
    op.create_index("ix_api_keys_tenant_id", "api_keys", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_api_keys_tenant_id", table_name="api_keys")
    op.drop_table("api_keys")
