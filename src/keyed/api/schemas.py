from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from keyed.core.models import AuthenticatedAPIKey


class PrincipalResponse(BaseModel):
    key_id: UUID
    tenant_id: UUID
    scopes: tuple[str, ...]
    key_prefix: str

    @classmethod
    def from_principal(cls, principal: AuthenticatedAPIKey) -> PrincipalResponse:
        return cls(
            key_id=principal.key_id,
            tenant_id=principal.tenant_id,
            scopes=principal.scopes,
            key_prefix=principal.key_prefix,
        )
