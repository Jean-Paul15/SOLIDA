# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

RUN groupadd --system --gid 999 solida \
 && useradd --system --gid 999 --uid 999 --create-home solida

# Bibliotheques systeme requises par WeasyPrint (rendu de la fiche PDF) : Pango/HarfBuzz,
# pas Cairo (retire des dependances de WeasyPrint depuis la v53). Liste minimale documentee
# pour une installation par wheels (doc.courtbouillon.org/weasyprint/stable/first_steps.html).
RUN apt-get update \
 && apt-get install --no-install-recommends -y \
    libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY backend/pyproject.toml backend/uv.lock ./
COPY modelisation /app/modelisation
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

COPY backend .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

ENV PATH="/app/backend/.venv/bin:$PATH"
ENTRYPOINT []
RUN chown -R solida:solida /app
USER solida

# --no-access-log : remplace par AccessLoggingMiddleware (JSON structure, adresse IP
# fiable via X-Real-IP) plutot que le journal texte brut d'uvicorn.
CMD ["uvicorn", "solida.infrastructure.application_fastapi:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
