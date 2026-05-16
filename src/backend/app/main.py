# backend/app/main.py
from contextlib import asynccontextmanager

from app.api.v1 import health, kds, menu, order, payment, seat, seed, webhook
from app.api.v1.admin import audit as admin_audit
from app.api.v1.admin import auth as admin_auth
from app.api.v1.admin import categories as admin_categories
from app.api.v1.admin import items as admin_items
from app.api.v1.admin import orders as admin_orders
from app.api.v1.admin import seats as admin_seats
from app.config import settings
from app.utils.timeout import start_timeout_worker, stop_timeout_worker
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    start_timeout_worker()
    # Run raw SQL migration for missing columns (defense in depth)
    await _run_startup_migration()
    yield
    # 关闭时
    stop_timeout_worker()


async def _run_startup_migration():
    """Add missing columns that may not exist from initial schema."""
    try:
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import create_async_engine

        db_url = settings.DATABASE_URL
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
            try:
                await conn.execute(
                    text(
                        """CREATE TABLE IF NOT EXISTS admin_audit_logs (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    admin_user_id UUID NOT NULL REFERENCES admin_users(id),
                    action VARCHAR(50) NOT NULL,
                    target_type VARCHAR(50) NOT NULL,
                    target_id VARCHAR(100) NOT NULL,
                    old_value JSONB,
                    new_value JSONB,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )"""
                    )
                )
            except Exception:
                pass
            await conn.commit()
        await engine.dispose()
    except Exception:
        pass  # Best-effort migration — don't block startup


app = FastAPI(
    title="Clap Cafe Ordering API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "Accept",
        "Origin",
    ],
)

# 健康检查
app.include_router(health.router, tags=["Health"])

# API v1 路由
app.include_router(menu.router, prefix="/v1", tags=["Menu"])
app.include_router(order.router, prefix="/v1", tags=["Orders"])
app.include_router(payment.router, prefix="/v1", tags=["Payments"])
app.include_router(seat.router, prefix="/v1", tags=["Seats"])
app.include_router(webhook.router, prefix="/v1", tags=["Webhooks"])
app.include_router(kds.router, prefix="/v1", tags=["KDS"])
app.include_router(seed.router, prefix="/v1", tags=["Admin"])

# Admin panel routes (protected by JWT)
app.include_router(admin_auth.router, prefix="/v1/admin", tags=["Admin Auth"])
app.include_router(
    admin_categories.router, prefix="/v1/admin/categories", tags=["Admin Categories"]
)
app.include_router(admin_items.router, prefix="/v1/admin/items", tags=["Admin Items"])
app.include_router(admin_seats.router, prefix="/v1/admin/seats", tags=["Admin Seats"])
app.include_router(
    admin_orders.router, prefix="/v1/admin/orders", tags=["Admin Orders"]
)
app.include_router(admin_audit.router, prefix="/v1/admin/audit", tags=["Admin Audit"])
