# backend/app/api/v1/kds.py
import asyncio
import json

import redis.asyncio as redis
from app.config import settings
from app.database import AsyncSessionLocal
from app.models import Order
from fastapi import APIRouter, Request
from sqlalchemy import select
from sse_starlette.sse import EventSourceResponse

router = APIRouter()

REDIS = redis.from_url(settings.REDIS_URL, decode_responses=True)


@router.get("/kds/orders/stream")
async def orders_stream(request: Request):
    async def event_generator():
        pubsub = REDIS.pubsub()
        await pubsub.subscribe("kds:orders")
        try:
            while True:
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1.0
                )
                if message and message["data"]:
                    yield {"event": "new_order", "data": message["data"]}
                yield {"event": "ping", "data": "pong"}
                await asyncio.sleep(5)
        finally:
            await pubsub.unsubscribe("kds:orders")
            await pubsub.close()

    return EventSourceResponse(event_generator())


@router.get("/kds/orders")
async def list_kds_orders():
    """返回所有 active 订单（submitted/confirmed/preparing/ready）"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Order)
            .where(Order.status.in_(["submitted", "confirmed", "preparing", "ready"]))
            .order_by(Order.created_at)
        )
        orders = result.scalars().all()
        return {
            "orders": [
                {
                    "id": o.id,
                    "seat_id": o.seat_id,
                    "status": o.status,
                    "payment_status": o.payment_status,
                    "created_at": o.created_at.isoformat() if o.created_at else None,
                    "items": [
                        {
                            "id": str(oi.id),
                            "item_name_zh": oi.item_name_zh,
                            "quantity": oi.quantity,
                            "options": oi.options,
                            "notes": oi.notes,
                            "print_group": oi.print_group,
                        }
                        for oi in o.items
                    ],
                }
                for o in orders
            ]
        }


@router.put("/kds/orders/{order_id}/status")
async def kds_update_status(order_id: str, status: str):
    """KDS 专用状态更新（走 Redis 发布）"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if not order:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="Order not found")

        order.status = status
        await db.commit()

        # 发布到 Redis
        await REDIS.publish(
            "kds:orders",
            json.dumps({"order_id": order_id, "status": status}),
        )
        return {"ok": True}
