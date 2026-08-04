# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

RUN groupadd --system --gid 999 solida \
 && useradd --system --gid 999 --uid 999 --create-home solida

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT []
RUN chown -R solida:solida /app
USER solida

CMD ["uvicorn", "solida.infrastructure.application_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]
