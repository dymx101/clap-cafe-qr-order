#!/bin/bash
set -e

echo "Patching DATABASE_URL for asyncpg..."
# Render provides postgresql://, we need postgresql+asyncpg://
export DATABASE_URL="${DATABASE_URL/postgresql:\/\//postgresql+asyncpg://}"

echo "Running database migrations..."
alembic upgrade head

echo "Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
