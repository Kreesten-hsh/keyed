from __future__ import annotations

from fastapi import APIRouter, Depends

from keyed.api.schemas import PrincipalResponse
from keyed.core.models import AuthenticatedAPIKey
from keyed.fastapi import KeyedAuth


def create_router(auth: KeyedAuth) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @router.get("/v1/whoami", response_model=PrincipalResponse)
    async def whoami(
        principal: AuthenticatedAPIKey = Depends(auth),
    ) -> PrincipalResponse:
        return PrincipalResponse.from_principal(principal)

    return router
