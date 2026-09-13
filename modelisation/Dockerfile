# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

WORKDIR /app/modelisation

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY modelisation/pyproject.toml modelisation/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --extra dev --extra mlops --extra notebooks --no-install-project

COPY modelisation /app/modelisation
COPY simulateur /app/simulateur
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --extra dev --extra mlops --extra notebooks

ENV PATH="/app/modelisation/.venv/bin:$PATH"
ENTRYPOINT ["solida-modele"]
