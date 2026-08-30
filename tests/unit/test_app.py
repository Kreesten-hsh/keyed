from __future__ import annotations

from uuid import uuid4

from httpx import ASGITransport, AsyncClient

from keyed.core.models import AuthenticatedAPIKey
from keyed.core.rate_limit import RateLimitDecision
from keyed.main import create_app


class FakeAuthenticator:
    async def authenticate(
        self,
        plaintext: str,
    ) -> tuple[AuthenticatedAPIKey, RateLimitDecision]:
        return (
            AuthenticatedAPIKey(
                key_id=uuid4(),
                tenant_id=uuid4(),
                scopes=("documents:read",),
                key_prefix="key_test_public.",
            ),
            RateLimitDecision(True, 60, 59, 0),
        )


async def test_health_route_is_public() -> None:
    app = create_app(FakeAuthenticator())

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_whoami_route_uses_keyed_auth() -> None:
    app = create_app(FakeAuthenticator())

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        missing = await client.get("/v1/whoami")
        accepted = await client.get("/v1/whoami", headers={"X-API-Key": "valid"})

    assert missing.status_code == 401
    assert accepted.status_code == 200
    assert set(accepted.json()) == {"key_id", "tenant_id", "scopes", "key_prefix"}
