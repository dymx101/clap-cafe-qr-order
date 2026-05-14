# backend/app/dependencies.py
from typing import Optional

from app.database import get_db
from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_seat_id(
    x_seat_id: Optional[str] = Header(None, alias="X-Seat-ID"),
    request: Request = None,
) -> str:
    """从请求头或URL参数获取座位号"""
    if x_seat_id:
        return x_seat_id
    seat = request.query_params.get("seat") if request else None
    if not seat:
        raise HTTPException(status_code=400, detail="Missing seat ID")
    return seat


async def get_db_session() -> AsyncSession:
    async for session in get_db():
        yield session
