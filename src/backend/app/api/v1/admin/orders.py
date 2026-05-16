# backend/app/api/v1/admin/orders.py
"""Admin CRUD endpoints for orders."""
import re
from datetime import datetime

from app.core.auth_service import get_current_admin
from app.core.order_service import (
    InvalidStatusTransitionError,
    OrderNotFoundError,
    OrderService,
)
from app.database import get_db
from app.models import Order, OrderItem
from app.models.admin_user import AdminUser
from app.schemas.admin import OrderAdminResponse, OrderListResponse, OrderNotesUpdate
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def _order_to_response(order) -> OrderAdminResponse:
    return OrderAdminResponse(
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


@router.get("/", response_model=OrderListResponse)
async def list_orders(
    status: str = Query(None, description="Filter by order status"),
    payment_status: str = Query(None, description="Filter by payment status"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """List all orders with optional status filters and pagination."""
    # Count total
    count_query = select(func.count(Order.id))
    if status:
        count_query = count_query.where(Order.status == status)
    if payment_status:
        count_query = count_query.where(Order.payment_status == payment_status)
    total_result = await db.execute(count_query)
    total_count = total_result.scalar() or 0

    # Fetch page
    offset = (page - 1) * limit
    query = select(Order).order_by(Order.created_at.desc()).offset(offset).limit(limit)
    if status:
        query = query.where(Order.status == status)
    if payment_status:
        query = query.where(Order.payment_status == payment_status)

    result = await db.execute(query)
    orders = result.scalars().all()

    return OrderListResponse(
        orders=[_order_to_response(o) for o in orders],
        total_count=total_count,
        page=page,
        limit=limit,
    )


@router.get("/{order_id}", response_model=OrderAdminResponse)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Get a single order by ID."""
    if not re.match(r"^CC-\d{8}-\d{3}$", order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID format")

    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")

    return _order_to_response(order)


@router.put("/{order_id}/notes", response_model=OrderAdminResponse)
async def update_order_notes(
    order_id: str,
    data: OrderNotesUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Update order notes (customer_notes or internal notes)."""
    if not re.match(r"^CC-\d{8}-\d{3}$", order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID format")

    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    order.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(order)
    return _order_to_response(order)


@router.post("/{order_id}/cancel", response_model=OrderAdminResponse)
async def admin_cancel_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Admin cancellation — only allowed for submitted orders."""
    if not re.match(r"^CC-\d{8}-\d{3}$", order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID format")

    svc = OrderService(db)
    try:
        order = await svc.cancel_order(order_id, reason="admin_cancelled")
        return _order_to_response(order)
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="ORDER_NOT_FOUND")
    except InvalidStatusTransitionError as e:
        raise HTTPException(status_code=422, detail=str(e))
