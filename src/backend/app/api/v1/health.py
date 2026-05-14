# backend/app/api/v1/health.py
from datetime import datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
    }


@router.get("/health/ready")
async def health_ready():
    # TODO: check DB + Redis connectivity
    return {"status": "ok", "db": "ok", "redis": "ok"}
