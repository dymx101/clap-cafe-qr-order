#!/bin/bash
set -e

echo "Patching DATABASE_URL for asyncpg..."
# Render provides postgresql://, we need postgresql+asyncpg://
export DATABASE_URL="${DATABASE_URL/postgresql:\/\//postgresql+asyncpg://}"

echo "Running database migrations..."
alembic upgrade head || echo "Alembic migration failed (may be already applied) — continuing..."

echo "Running raw SQL migration fallback (add missing columns if not exists)..."
python - <<'PYEOF'
import asyncio, os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

async def migrate():
    db_url = os.environ.get("DATABASE_URL", "")
    engine = create_async_engine(db_url, echo=False)
    async with engine.connect() as conn:
        for stmt in [
            "ALTER TABLE items ADD COLUMN IF NOT EXISTS low_stock_threshold INTEGER NOT NULL DEFAULT 5",
            "ALTER TABLE admin_users ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR(255)",
            "ALTER TABLE admin_users ADD COLUMN IF NOT EXISTS password_reset_expires TIMESTAMPTZ",
        ]:
            try:
                await conn.execute(text(stmt))
            except Exception:
                pass
        # admin_audit_logs table
        try:
            await conn.execute(text("""CREATE TABLE IF NOT EXISTS admin_audit_logs (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                admin_user_id UUID NOT NULL REFERENCES admin_users(id),
                action VARCHAR(50) NOT NULL,
                target_type VARCHAR(50) NOT NULL,
                target_id VARCHAR(100) NOT NULL,
                old_value JSONB,
                new_value JSONB,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )"""))
        except Exception:
            pass
        await conn.commit()
    await engine.dispose()

asyncio.run(migrate())
echo "Raw SQL migration complete."

echo "Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
