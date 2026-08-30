# Installation & Setup

## Requirements

* Python `>= 3.11`
* PostgreSQL `>= 14`
* FastAPI `>= 0.115`

---

## 1. Package Installation

Install `keyed-api-auth` in your Python environment:

```bash
pip install keyed-api-auth
```

Or when developing locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

---

## 2. Environment Configuration

Define your PostgreSQL connection string in your environment (or `.env` file):

```bash
export KEYED_DATABASE_URL="postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/keyed"
```

---

## 3. Database Migrations

Apply the Alembic schema migrations to create the `api_keys` table:

```bash
alembic upgrade head
```

---

## 4. Run with Docker Compose (Optional)

If you prefer running a local isolated stack with PostgreSQL and FastAPI ready to go:

```bash
cp .env.example .env
docker compose up --build
```

The service will start on `http://127.0.0.1:58000`:
* `GET /health` : Public health check (`200 OK`)
* `GET /v1/whoami` : Sample protected route (`401 Unauthorized` without a valid key)
