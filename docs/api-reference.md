# API Reference

The `Keyed` class is the primary integration point for the library.

```python
from keyed import Keyed

keyed = Keyed(database_url="postgresql+asyncpg://user:pass@host:5432/db")
```

---

## 1. Authentication Dependency

### `keyed.auth.require_scopes(*scopes: str)`

Creates a FastAPI dependency that extracts `X-API-Key`, enforces sliding-window rate limits, verifies the hash in constant time, and asserts that the key possesses all specified scopes.

```python
@app.get("/analytics")
async def get_analytics(
    principal: AuthenticatedAPIKey = Depends(
        keyed.auth.require_scopes("analytics:read", "reports:read")
    ),
):
    return {"tenant_id": str(principal.tenant_id), "scopes": principal.scopes}
```

* **Headers:** `X-API-Key: <plaintext_key>`
* **Success:** Injects `AuthenticatedAPIKey` (contains `id`, `tenant_id`, `name`, `scopes`, `environment`).
* **Errors:**
  * `401 Unauthorized`: Missing, expired, revoked, or invalid key format/hash.
  * `403 Forbidden`: Key is valid but lacks one of the required scopes.
  * `429 Too Many Requests`: Exceeded `rate_limit_per_minute` (includes `Retry-After: <seconds>`).

---

## 2. Key Management

### `keyed.issue_key(...)`

Generates and persists a new cryptographically secure API key.

```python
issued = await keyed.issue_key(
    tenant_id=UUID("..."),
    name="Production Agent Key",
    scopes=["documents:read", "documents:write"],
    rate_limit_per_minute=120,
    expires_at=None,
    environment="live", # or "test"
)

# Access plaintext (returned only here, never stored)
print(issued.plaintext) # e.g. key_live_abc123...
print(issued.id)        # UUID primary key
print(issued.prefix)    # e.g. key_live_abc1
```

### `keyed.revoke_key(key_id: UUID, tenant_id: UUID)`

Instantly revokes an API key in PostgreSQL. Future requests using this key will immediately return `401 Unauthorized`.

```python
await keyed.revoke_key(key_id=key_uuid, tenant_id=tenant_uuid)
```

---

## 3. Rate Limiting Behavior

The in-process sliding window monitors request timestamps per key in memory:
* **Latency:** `< 1ms` check overhead.
* **Scope:** In-process counters (single-worker per process). 
* **Header:** Returns `Retry-After` indicating the remaining wait time in seconds before the window resets.
