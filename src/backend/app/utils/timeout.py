# backend/app/utils/timeout.py
import asyncio
from datetime import datetime, timedelta

from app.config import settings
from app.database import AsyncSessionLocal
from app.models import Order, OrderStatus, PaymentStatus, Seat
from sqlalchemy import and_, select, update


async def check_unpaid_orders():
    """定时任务：取消超时的未支付订单"""
    async with AsyncSessionLocal() as db:
        cutoff = datetime.utcnow() - timedelta(
            minutes=settings.STRIPE_PAYMENT_TIMEOUT_MINUTES
        )
        result = await db.execute(
            select(Order)
            .where(
                and_(
                    Order.payment_status == PaymentStatus.PENDING.value,
                    Order.status == OrderStatus.SUBMITTED.value,
                    Order.created_at < cutoff,
                )
            )
            .with_for_update(skip_locked=True)
        )
        for order in result.scalars():
            order.status = OrderStatus.CANCELLED.value
            order.payment_status = PaymentStatus.CANCELLED.value
            order.cancelled_at = datetime.utcnow()
            await db.execute(
                update(Seat).where(Seat.id == order.seat_id).values(status="vacant")
            )
            await db.commit()


def start_timeout_worker():
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(_timeout_loop())
    except RuntimeError:
        pass  # no running loop yet


async def _timeout_loop():
    while True:
        await asyncio.sleep(60)
        try:
            await check_unpaid_orders()
        except Exception as e:
            print(f"Timeout worker error: {e}")


def stop_timeout_worker():
    pass
