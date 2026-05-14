# backend/app/utils/order_id.py
from datetime import date

from app.models import Order
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def generate_order_id(db: AsyncSession) -> str:
    """生成当日订单号：CC-YYYYMMDD-NNN"""
    today = date.today()
    prefix = f"CC-{today.strftime('%Y%m%d')}-"

    result = await db.execute(
        select(func.max(Order.id)).where(Order.id.like(f"{prefix}%"))
    )
    max_id = result.scalar_one_or_none()

    if max_id:
        try:
            nnn = int(max_id.split("-")[-1]) + 1
        except (ValueError, IndexError):
            nnn = 1
    else:
        nnn = 1

    return f"{prefix}{nnn:03d}"
