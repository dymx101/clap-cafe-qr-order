# backend/app/api/v1/order.py
import uuid as uuid_lib

from app.core.order_service import (
    InvalidStatusTransitionError,
    ItemOutOfStockError,
    OrderNotFoundError,
    OrderService,
    SeatNotVacantError,
)
from app.database import get_db
from app.models import ORDER_STATUS_TRANSITIONS
from app.schemas.order import (
    OrderCancelRequest,
    OrderCreate,
    OrderRejectRequest,
    OrderResponse,
    OrderStatusResponse,
    OrderStatusUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def _order_to_response(order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        seat_id=order.seat_id,
        status=order.status,
        payment_status=order.payment_status,
        payment_method=order.payment_method,
        payment_intent_id=order.payment_intent_id,
        items=[
            {
                "id": str(oi.id),
                "item_id": str(oi.item_id),
                "item_name_zh": oi.item_name_zh,
                "item_name_en": oi.item_name_en,
                "quantity": oi.quantity,
                "unit_price": float(oi.unit_price),
                "options": oi.options or {},
                "notes": oi.notes,
                "print_group": oi.print_group,
            }
            for oi in order.items
        ],
        subtotal_sgd=float(order.subtotal_sgd),
        tax_sgd=float(order.tax_sgd),
        total_sgd=float(order.total_sgd),
        notes=order.notes,
        customer_notes=order.customer_notes,
        rejected_reason=order.rejected_reason,
        created_at=order.created_at,
        updated_at=order.updated_at,
        paid_at=order.paid_at,
        completed_at=order.completed_at,
        cancelled_at=order.cancelled_at,
    )


@router.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
):
    svc = OrderService(db)
    try:
        order = await svc.create_order(
            seat_id=order_data.seat_id,
            items=[
                {
                    "item_id": it.item_id,
                    "quantity": it.quantity,
                    "options": it.options or {},
                    "notes": it.notes,
                }
                for it in order_data.items
            ],
            customer_notes=order_data.customer_notes,
        )
        return _order_to_response(order)
    except OrderNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SeatNotVacantError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ItemOutOfStockError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
):
    import re

    if not re.match(r"^CC-\d{8}-\d{3}$", order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID format")
    svc = OrderService(db)
    try:
        order = await svc.get_order_or_404(order_id)
        return _order_to_response(order)
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")


@router.get("/orders/{order_id}/status", response_model=OrderStatusResponse)
async def get_order_status(
    order_id: str,
    db: AsyncSession = Depends(get_db),
):
    import re

    if not re.match(r"^CC-\d{8}-\d{3}$", order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID format")
    svc = OrderService(db)
    try:
        order = await svc.get_order_or_404(order_id)
        return OrderStatusResponse(
            id=order.id,
            status=order.status,
            payment_status=order.payment_status,
            updated_at=order.updated_at,
        )
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")


@router.put("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    data: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    svc = OrderService(db)
    try:
        order = await svc.update_status(order_id, data.status)
        return _order_to_response(order)
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")
    except InvalidStatusTransitionError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/orders/{order_id}/reject", response_model=OrderResponse)
async def reject_order(
    order_id: str,
    data: OrderRejectRequest,
    db: AsyncSession = Depends(get_db),
):
    svc = OrderService(db)
    try:
        order = await svc.reject_order(order_id, data.reason, data.items)
        return _order_to_response(order)
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")


@router.post("/orders/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    data: OrderCancelRequest,
    db: AsyncSession = Depends(get_db),
):
    svc = OrderService(db)
    try:
        order = await svc.cancel_order(order_id, data.reason)
        return _order_to_response(order)
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")
    except InvalidStatusTransitionError as e:
        raise HTTPException(status_code=422, detail=str(e))
