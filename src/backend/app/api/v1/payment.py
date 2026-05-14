# backend/app/api/v1/payment.py
from app.core.order_service import OrderNotFoundError, OrderService
from app.core.payment_service import PaymentService
from app.database import get_db
from app.schemas.payment import (
    PaymentIntentCreate,
    PaymentIntentResponse,
    PaymentStatusResponse,
    PayNowConfirmRequest,
    PayNowConfirmResponse,
)
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/payments/create-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    data: PaymentIntentCreate,
    db: AsyncSession = Depends(get_db),
):
    svc = OrderService(db)
    try:
        order = await svc.get_order_or_404(data.order_id)
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")

    ps = PaymentService()
    amount_cents = int(float(order.total_sgd) * 100)

    try:
        intent = ps.create_payment_intent(
            order_id=order.id,
            amount_cents=amount_cents,
            metadata={"seat_id": order.seat_id},
            payment_method_types=data.payment_method_types,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 更新订单 payment_intent_id
    order.payment_intent_id = intent.id
    await db.commit()

    return PaymentIntentResponse(
        client_secret=intent.client_secret,
        payment_intent_id=intent.id,
        amount=intent.amount,
        currency=intent.currency,
    )


@router.post("/payments/confirm-paynow", response_model=PayNowConfirmResponse)
async def confirm_paynow(
    data: PayNowConfirmRequest,
    db: AsyncSession = Depends(get_db),
):
    """从已创建的 PaymentIntent 获取 PayNow QR 信息"""
    ps = PaymentService()
    try:
        order_svc = OrderService(db)
        order = await order_svc.get_order_or_404(data.order_id)
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")

    if not order.payment_intent_id:
        raise HTTPException(
            status_code=400, detail="No payment intent found for this order"
        )

    try:
        intent = ps.retrieve_payment_intent(order.payment_intent_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if (
        not intent._next_action
        or not intent.next_action.display_bank_transfer_instructions
    ):
        raise HTTPException(status_code=400, detail="PayNow QR not available")

    instructions = intent.next_action.display_bank_transfer_instructions
    return PayNowConfirmResponse(
        paynow_qr_url=instructions.qr_code_url or "",
        paynow_reference=instructions.reference_number or order.id.replace("-", ""),
        expires_at=intent.expires_at,
    )


@router.get(
    "/payments/{payment_intent_id}/status", response_model=PaymentStatusResponse
)
async def get_payment_status(payment_intent_id: str):
    ps = PaymentService()
    try:
        intent = ps.retrieve_payment_intent(payment_intent_id)
        return PaymentStatusResponse(status=intent.status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
