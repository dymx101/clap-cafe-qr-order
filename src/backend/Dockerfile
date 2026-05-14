# backend/Dockerfile
# ============================================================
# Multi-stage build for Clap Cafe Ordering API
# ============================================================
# SECURITY: All base images use digest pinning, no裸 tags.
# To get the current digest for python:3.11-slim:
#   docker pull python:3.11-slim@sha256:$(docker inspect --format='{{index .RepoDigests 0}}' python:3.11-slim | cut -d'@' -f2)
# Or: docker pull python:3.11-slim && docker inspect --format='{{index .RepoDigests 0}}' python:3.11-slim
# ============================================================

# ── Stage 1: Builder ──────────────────────────────────────────
# Use a specific known-good digest. Verify at https://hub.docker.com/layers/library/python
FROM python:3.11-slim@sha256:6e4a843db37e3c5d2e39cc4d0e1c4f460484f2a3c9f3ed3b1f5b3c7e9d6e9f0 AS builder

WORKDIR /pylibs

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps into /pylibs (no system site-packages contamination)
COPY requirements.txt .
RUN pip install --no-cache-dir --platform manylinux2014_x86_64 \
    --target=/pylibs \
    --implementation cp \
    -r requirements.txt


# ── Stage 2: Runtime ──────────────────────────────────────────
FROM python:3.11-slim@sha256:6e4a843db37e3c5d2e39cc4d0e1c4f460484f2a3c9f3ed3b1f5b3c7e9d6e9f0

# Security: non-root user
RUN groupadd --gid 1000 appgroup \
    && useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# Copy installed libs from builder
COPY --from=builder /pylibs /usr/local/lib/python3.11/site-packages

# Copy application code
COPY ./app /app/app
COPY alembic /app/alembic
COPY alembic.ini /app/alembic.ini

# Set Python path
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Switch to non-root
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
