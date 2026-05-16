# backend/app/api/v1/health.py
from datetime import datetime

import redis.asyncio as redis
from app.config import settings
from app.database import engine
from fastapi import APIRouter

router = APIRouter()

_redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
    }


@router.get("/health/ready")
async def health_ready():
    db_ok = False
    redis_ok = False

    # DB check — run a lightweight query
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    # Redis check — PING
    try:
        await _redis_client.ping()
        redis_ok = True
    except Exception:
        pass

    status = "ok" if (db_ok and redis_ok) else "fail"
    code = 200 if status == "ok" else 503

    return {
        "status": status,
        "checks": {
            "database": "ok" if db_ok else "fail",
            "redis": "ok" if redis_ok else "fail",
        },
    }
