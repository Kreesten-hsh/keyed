# keyed

`keyed` is a local FastAPI authentication library for generated API keys. It stores only salted hashes in PostgreSQL, checks scopes, supports immediate revocation and applies an in-process sliding-window rate limit.

## Project layout

```text
src/keyed/api/       FastAPI routes and response schemas
src/keyed/core/      Hashing, scopes, service and rate limiter
src/keyed/db/        SQLAlchemy models, sessions and repository
src/keyed/fastapi.py Public FastAPI dependency integration
alembic/             PostgreSQL migrations
tests/unit/          Tests without a database
tests/integration/   Full PostgreSQL authentication cycles
```

## Run with Docker

Create a local `.env` from `.env.example` and set every blank value. Use local-only PostgreSQL credentials and ports that are free on the machine.

```bash
docker compose up --build
```

The app applies Alembic migrations before starting. `GET /health` is public and `GET /v1/whoami` requires `X-API-Key`.

## Run locally

Python 3.11 or newer and PostgreSQL are required.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
export KEYED_DATABASE_URL='postgresql+asyncpg://<user>:<password>@127.0.0.1:5432/<database>'
alembic upgrade head
uvicorn keyed.main:create_app --factory --reload
```

## Integrate with FastAPI

`Keyed` is the single public entry point. The plaintext key is returned only by `issue_key()` and must be shown once through a secure channel. Do not log it.

```python
import os
from uuid import UUID

from fastapi import Depends, FastAPI

from keyed import Keyed
from keyed.core.models import AuthenticatedAPIKey

app = FastAPI()
keyed = Keyed(os.environ["KEYED_DATABASE_URL"])


@app.get("/documents")
async def list_documents(
    principal: AuthenticatedAPIKey = Depends(
        keyed.auth.require_scopes("documents:read")
    ),
) -> dict[str, str]:
    return {"tenant_id": str(principal.tenant_id)}


async def provision_key(tenant_id: UUID) -> str:
    issued = await keyed.issue_key(
        tenant_id=tenant_id,
        scopes=["documents:read"],
        rate_limit_per_minute=60,
        environment="live",
    )
    return issued.plaintext
```

Revoke with `await keyed.revoke_key(key_id, tenant_id)`. Revocation is checked against PostgreSQL on the next request.

## Rate limiter limitation

The default sliding-window counters live in the application process. They are lost on restart and are not shared across multiple workers. Run one worker during the beta if a strict per-key quota is required.

## Tests

Unit tests:

```bash
pytest tests/unit -q
```

Full suite against the Docker PostgreSQL service:

```bash
docker compose --profile test run --rm test
```

Quality checks:

```bash
ruff check src tests alembic
ruff format --check src tests alembic
mypy src/keyed
```
