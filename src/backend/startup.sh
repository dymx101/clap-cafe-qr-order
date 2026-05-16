#!/bin/bash

echo "Patching DATABASE_URL for asyncpg..."
export DATABASE_URL="${DATABASE_URL/postgresql:\/\//postgresql+asyncpg://}"

echo "Running database migrations..."
alembic upgrade head || echo "Alembic migration done or already applied"

echo "Running raw SQL migration fallback..."
python - <<'PYEOF'
import asyncio, os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def migrate():
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        return

    engine = create_async_engine(db_url, echo=False)
    async with engine.connect() as conn:
        stmts = [
            ("items.low_stock_threshold",
             "ALTER TABLE items ADD COLUMN IF NOT EXISTS low_stock_threshold INTEGER NOT NULL DEFAULT 5"),
            ("admin_users.password_reset_token",
             "ALTER TABLE admin_users ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR(255)"),
            ("admin_users.password_reset_expires",
             "ALTER TABLE admin_users ADD COLUMN IF NOT EXISTS password_reset_expires TIMESTAMPTZ"),
        ]
        for col_name, sql in stmts:
            try:
                await conn.execute(text(sql))
                print(f"  {col_name}: added")
            except Exception as e:
                err_str = str(e).lower()
                if "duplicate" in err_str or "already exists" in err_str:
                    print(f"  {col_name}: already exists (skipped)")
                else:
                    print(f"  {col_name}: {e}")

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
            print("  admin_audit_logs table: created")
        except Exception as e:
            if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
                print("  admin_audit_logs table: already exists (skipped)")
            else:
                print(f"  admin_audit_logs: {e}")

        await conn.commit()
    await engine.dispose()
    print("Raw SQL migration complete.")

asyncio.run(migrate())
PYEOF

echo "Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
