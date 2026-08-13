# =========================================================
# Enterprise AI Business Decision Intelligence Platform
# Backend Dockerfile (FastAPI + Celery share this image)
# =========================================================

FROM python:3.12-slim AS base

# ---------------------------------------------------------
# System dependencies
# psycopg2 needs libpq; some ML/PDF libs need build tools.
# ---------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ---------------------------------------------------------
# Python dependencies (cached as its own layer)
# ---------------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------
# Application code
# (datasets/, knowledge_base/, outputs/, saved_models/,
# vector_db/, logs/, reports/ are NOT copied here — they're
# mounted as volumes by docker-compose so the image stays
# small and the data persists/updates without a rebuild.)
# ---------------------------------------------------------
COPY backend/ backend/
COPY agents/ agents/
COPY rag/ rag/
COPY config/ config/
COPY alembic/ alembic/
COPY alembic.ini .
COPY dashboards/ dashboards/

# Writable runtime directories the app expects to exist,
# even before the corresponding volumes are mounted.
RUN mkdir -p logs outputs reports saved_models vector_db data figures \
    datasets knowledge_base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default process is the API; docker-compose overrides `command`
# for the celery worker/beat services that reuse this same image.
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
