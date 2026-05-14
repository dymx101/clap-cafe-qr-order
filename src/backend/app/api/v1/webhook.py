# backend/app/api/v1/webhook.py
from datetime import datetime

from app.database import AsyncSessionLocal
from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select

router = APIRouter()


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """处理 Stripe Webhook 回调"""
    from app.core.order_service import OrderService
    from app.core.payment_service import PaymentService
    from app.models import Order, OrderStatus, PaymentStatus

    body = await request.body()
    sig = request.headers.get("stripe-signature", "")

    ps = PaymentService()
    try:
        event = await ps.construct_webhook_event_async(body, sig)
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Webhook signature verification failed: {e}"
        )

    async with AsyncSessionLocal() as db:
        order_svc = OrderService(db)

        if event["type"] == "payment_intent.succeeded":
            intent = event["data"]["object"]
            pi_id = intent["id"]
            order_result = await db.execute(
                select(Order).where(Order.payment_intent_id == pi_id)
            )
            order = order_result.scalar_one_or_none()
            if not order:
                return {"received": True}

            # 幂等
            if order.payment_status == PaymentStatus.PAID.value:
                return {"received": True}

            order.payment_status = PaymentStatus.PAID.value
            order.status = OrderStatus.CONFIRMED.value
            order.paid_at = datetime.utcnow()
            order.updated_at = datetime.utcnow()
            await db.commit()

        elif event["type"] == "payment_intent.payment_failed":
            intent = event["data"]["object"]
            pi_id = intent["id"]
            order_result = await db.execute(
                select(Order).where(Order.payment_intent_id == pi_id)
            )
            order = order_result.scalar_one_or_none()
            if order:
                order.payment_status = PaymentStatus.FAILED.value
                await db.commit()

        elif event["type"] == "payment_intent.canceled":
            intent = event["data"]["object"]
            pi_id = intent["id"]
            order_result = await db.execute(
                select(Order).where(Order.payment_intent_id == pi_id)
            )
            order = order_result.scalar_one_or_none()
            if order:
                order.payment_status = PaymentStatus.CANCELLED.value
                order.status = OrderStatus.CANCELLED.value
                await db.commit()

    return {"received": True}
