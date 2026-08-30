FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY alembic.ini ./
COPY alembic ./alembic

FROM base AS runtime

RUN python -m pip install --no-cache-dir .

CMD ["sh", "-c", "alembic upgrade head && uvicorn keyed.main:create_app --factory --host 0.0.0.0 --port 8000"]

FROM base AS test

COPY tests ./tests

RUN python -m pip install --no-cache-dir '.[dev]'

CMD ["sh", "-c", "alembic upgrade head && pytest --cov=keyed --cov-report=term-missing"]
