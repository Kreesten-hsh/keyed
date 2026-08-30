# Quickstart

`keyed` is a lightweight local FastAPI authentication library for issuing, verifying, and rate-limiting API keys. All validation happens in-process and against your own PostgreSQL database with zero external cloud proxies.

---

## 5-Minute Example

```python
import os
from uuid import UUID

from fastapi import Depends, FastAPI
from keyed import Keyed
from keyed.core.models import AuthenticatedAPIKey

app = FastAPI(title="My Protected API")

# Initialize keyed with your PostgreSQL database URL
keyed = Keyed(os.environ["KEYED_DATABASE_URL"])


# Protect any route with scopes and automatic rate-limiting
@app.get("/v1/documents")
async def list_documents(
    principal: AuthenticatedAPIKey = Depends(
        keyed.auth.require_scopes("documents:read")
    ),
) -> dict[str, str]:
    return {"tenant_id": str(principal.tenant_id), "status": "authorized"}


# Issue an API key for a client (run via script, seed, or onboarding endpoint)
async def create_client_key(tenant_id: UUID) -> str:
    issued = await keyed.issue_key(
        tenant_id=tenant_id,
        scopes=["documents:read"],
        rate_limit_per_minute=60,
        environment="live",
    )
    # The plaintext is returned only once at creation
    return issued.plaintext
```

---

## What Happens on Each Request

1. **Header Extraction:** `keyed` reads the incoming `X-API-Key` header.
2. **In-Memory Rate Limiting:** Checks sliding-window counters in process memory. Returns `429 Too Many Requests` with a `Retry-After` header if exceeded.
3. **Constant-Time Verification:** Looks up the key by its dynamic prefix, retrieves the salted SHA-256 hash from PostgreSQL, and compares using `hmac.compare_digest`.
4. **Scope & Revocation Check:** Ensures the key is not expired, not revoked, and holds the required scopes before executing your route logic.
