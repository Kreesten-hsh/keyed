from __future__ import annotations

from uuid import uuid4

from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from keyed.core.errors import InvalidAPIKeyError, RateLimitExceededError
from keyed.core.models import AuthenticatedAPIKey
from keyed.core.rate_limit import RateLimitDecision
from keyed.fastapi import KeyedAuth


class FakeAuthenticator:
    def __init__(self) -> None:
        self.error: Exception | None = None
        self.principal = AuthenticatedAPIKey(
            key_id=uuid4(),
            tenant_id=uuid4(),
            scopes=("documents:read",),
            key_prefix="key_test_public.",
        )

    async def authenticate(
        self,
        plaintext: str,
    ) -> tuple[AuthenticatedAPIKey, RateLimitDecision]:
        if self.error is not None:
            raise self.error
        return self.principal, RateLimitDecision(True, 10, 9, 0)


def create_test_app(authenticator: FakeAuthenticator) -> FastAPI:
    app = FastAPI()
    auth = KeyedAuth(authenticator)

    @app.get("/read")
    async def read_documents(
        principal: AuthenticatedAPIKey = Depends(auth.require_scopes("documents:read")),
    ) -> dict[str, str]:
        return {"tenant_id": str(principal.tenant_id)}

    @app.post("/write")
    async def write_documents(
        principal: AuthenticatedAPIKey = Depends(auth.require_scopes("documents:write")),
    ) -> dict[str, str]:
        return {"tenant_id": str(principal.tenant_id)}

    return app


async def test_missing_key_returns_401() -> None:
    app = create_test_app(FakeAuthenticator())

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/read")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "ApiKey"
    assert response.json() == {"detail": "Invalid API key"}


async def test_valid_key_returns_principal_and_rate_headers() -> None:
    app = create_test_app(FakeAuthenticator())

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/read", headers={"X-API-Key": "valid"})

    assert response.status_code == 200
    assert response.headers["x-ratelimit-limit"] == "10"
    assert response.headers["x-ratelimit-remaining"] == "9"


async def test_invalid_or_revoked_key_returns_same_401() -> None:
    authenticator = FakeAuthenticator()
    authenticator.error = InvalidAPIKeyError()
    app = create_test_app(authenticator)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/read", headers={"X-API-Key": "invalid"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API key"}


async def test_missing_scope_returns_403() -> None:
    app = create_test_app(FakeAuthenticator())

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/write", headers={"X-API-Key": "valid"})

    assert response.status_code == 403
    assert response.json() == {"detail": "Insufficient API key scope"}


async def test_rate_limit_returns_429_with_retry_after() -> None:
    authenticator = FakeAuthenticator()
    authenticator.error = RateLimitExceededError(RateLimitDecision(False, 10, 0, 17))
    app = create_test_app(authenticator)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/read", headers={"X-API-Key": "limited"})

    assert response.status_code == 429
    assert response.headers["retry-after"] == "17"
    assert response.headers["x-ratelimit-limit"] == "10"
    assert response.headers["x-ratelimit-remaining"] == "0"
