# keyed

`keyed` is a local FastAPI authentication library for generated API keys. It stores only salted hashes in PostgreSQL, checks scopes, supports immediate revocation and applies an in-process sliding-window rate limit.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![Alembic](https://img.shields.io/badge/Alembic-Migrations-6BA81E)](https://alembic.sqlalchemy.org)
[![Pydantic](https://img.shields.io/badge/Pydantic-E92063?logo=pydantic&logoColor=white)](https://docs.pydantic.dev)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com)
[![pytest](https://img.shields.io/badge/pytest-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy: checked](https://img.shields.io/badge/mypy-checked-2A6DB2)](https://mypy-lang.org)

## Why keyed

`keyed` handles API key authentication directly inside your FastAPI application and PostgreSQL database.
It issues generated keys, stores only salted hashes, verifies scopes, enforces immediate revocation, and applies per-key sliding-window rate limits.
All checks run in-process without network round trips to an external cloud proxy or third-party service.

## Quickstart

`Keyed` is the single public entry point. The plaintext key is returned only once by `issue_key()` and must be shown immediately to the user through a secure channel. Do not persist or log plaintext keys.

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

Revoke keys instantly with `await keyed.revoke_key(key_id, tenant_id)`. Revocation is verified against PostgreSQL on the next incoming request.

## Installation

### Run with Docker

Create a local `.env` from `.env.example` and populate the required database settings.

```bash
docker compose up --build
```

The application runs Alembic migrations automatically before starting the server. `GET /health` is public and `GET /v1/whoami` requires an `X-API-Key` header.

### Run locally

Python 3.11 or newer and a running PostgreSQL instance are required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
export KEYED_DATABASE_URL='postgresql+asyncpg://<user>:<password>@127.0.0.1:5432/<database>'
alembic upgrade head
uvicorn keyed.main:create_app --factory --reload
```

## Project layout

```text
src/keyed/api/       FastAPI routes and response schemas
src/keyed/core/      Hashing, scopes, service and rate limiter
src/keyed/db/        SQLAlchemy models, sessions and repository
src/keyed/fastapi.py Public FastAPI dependency integration
alembic/             PostgreSQL schema migrations
tests/unit/          Unit tests without a database dependency
tests/integration/   Integration tests with PostgreSQL
docs/                MkDocs documentation sources
```

## Documentation

Documentation sources are located in `docs/`. Preview the documentation locally with MkDocs:

```bash
mkdocs serve
```

The documentation server will start at `http://127.0.0.1:8000/`. When the API is running locally with Uvicorn, FastAPI also exposes interactive OpenAPI documentation at `http://127.0.0.1:8000/docs`.

## Rate limiter limitation

The default sliding-window counters live in the application process memory. They reset on server restart and are not shared across multiple processes. Run a single worker process during the beta if strict per-key quotas are required.

## Tests

Run the unit test suite:

```bash
pytest tests/unit -q
```

Run the full integration test suite with Docker:

```bash
docker compose --profile test run --rm test
```

Run static analysis and code formatting checks:

```bash
ruff check src tests alembic
ruff format --check src tests alembic
mypy src/keyed
```

## Status

The core implementation is functional and tested in local unit and integration suites. Beta tester recruitment is currently starting, with zero external testers confirmed to date. The immediate milestone is validating staging integrations with FastAPI developers and evaluating usage retention over seven days.

## License

This project is licensed under the terms of the MIT license. See the [LICENSE](LICENSE) file for details.
