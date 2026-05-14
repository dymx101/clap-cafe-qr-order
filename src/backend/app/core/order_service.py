# backend/app/core/order_service.py
import hashlib
import re
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

import redis.asyncio as redis
from app.config import settings
from app.models import (
    ORDER_STATUS_TRANSITIONS,
    Category,
    Item,
    Order,
    OrderItem,
    OrderStatus,
    PaymentStatus,
    Seat,
)
from app.utils.order_id import generate_order_id
from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

REDIS = redis.from_url(settings.REDIS_URL, decode_responses=True)

TAX_RATE = Decimal("0.09")

# 订单去重缓存时间（秒）
ORDER_DEDUP_TTL = 300


class OrderNotFoundError(Exception):
    pass


class SeatNotVacantError(Exception):
    pass


class InvalidStatusTransitionError(Exception):
    pass


class ItemOutOfStockError(Exception):
    pass


def _options_key(seat_id: str, items: list) -> str:
    """生成订单去重key"""
    raw = f"{seat_id}::{hashlib.md5(str(items).encode()).hexdigest()}"
    return f"order:dedup:{raw}"


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(
        self,
        seat_id: str,
        items: list,
        customer_notes: Optional[str] = None,
        lang: str = "zh",
    ) -> Order:
        # 1. 座位校验
        seat_result = await self.db.execute(select(Seat).where(Seat.id == seat_id))
        seat = seat_result.scalar_one_or_none()
        if not seat:
            raise OrderNotFoundError(f"Seat {seat_id} not found")
        if seat.status != "vacant":
            raise SeatNotVacantError(
                f"Seat {seat_id} is not vacant (current: {seat.status})"
            )

        # 2. 去重检查
        dedup_key = _options_key(seat_id, items)
        cached_order_id = await REDIS.get(dedup_key)
        if cached_order_id:
            exist = await self.db.execute(
                select(Order).where(Order.id == cached_order_id)
            )
            existing_order = exist.scalar_one_or_none()
            if existing_order:
                return existing_order

        # 3. 库存校验 + 价格快照
        item_ids = [it["item_id"] for it in items]
        item_result = await self.db.execute(
            select(Item).where(
                Item.id.in_([uuid.UUID(i) for i in item_ids]), Item.is_available == True
            )
        )
        item_map = {str(it.id): it for it in item_result.scalars().all()}

        order_items = []
        subtotal = Decimal("0")
        for it in items:
            item = item_map.get(it.item_id)
            if not item:
                raise ValueError(f"Item {it.item_id} not found or unavailable")
            if item.stock is not None and item.stock < it.quantity:
                raise ItemOutOfStockError(f"Item {item.name_zh} stock insufficient")
            price = Decimal(str(item.price_sgd))
            subtotal += price * it.quantity
            order_items.append(
                {
                    "item_id": uuid.UUID(it.item_id),
                    "item_name_zh": item.name_zh,
                    "item_name_en": item.name_en,
                    "quantity": it.quantity,
                    "unit_price": price,
                    "options": it.options,
                    "notes": it.notes,
                    "print_group": "food" if _is_food(item.category_id) else "drink",
                }
            )

        # 4. 扣减库存
        for it in items:
            item = item_map[it.item_id]
            if item.stock is not None:
                item.stock -= it.quantity

        tax = (subtotal * TAX_RATE).quantize(Decimal("0.01"))
        total = subtotal + tax

        # 5. 生成订单号
        order_id = await generate_order_id(self.db)

        # 6. 创建订单
        order = Order(
            id=order_id,
            seat_id=seat_id,
            status=OrderStatus.SUBMITTED.value,
            payment_status=PaymentStatus.PENDING.value,
            subtotal_sgd=subtotal,
            tax_sgd=tax,
            total_sgd=total,
            notes=None,
            customer_notes=customer_notes,
        )
        self.db.add(order)

        for oi in order_items:
            self.db.add(OrderItem(order_id=order_id, **oi))

        # 7. 座位设为 occupied
        seat.status = "occupied"

        await self.db.commit()
        await self.db.refresh(order)

        # 8. 缓存去重key
        await REDIS.setex(dedup_key, ORDER_DEDUP_TTL, order_id)

        return order

    async def get_order(self, order_id: str) -> Optional[Order]:
        result = await self.db.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()

    async def get_order_or_404(self, order_id: str) -> Order:
        order = await self.get_order(order_id)
        if not order:
            raise OrderNotFoundError(f"Order {order_id} not found")
        return order

    async def update_status(self, order_id: str, new_status: str) -> Order:
        order = await self.get_order_or_404(order_id)
        current = OrderStatus(order.status)
        try:
            target = OrderStatus(new_status)
        except ValueError:
            raise ValueError(f"Invalid status: {new_status}")

        if target not in ORDER_STATUS_TRANSITIONS.get(current, set()):
            raise InvalidStatusTransitionError(
                f"Cannot transition from {current.value} to {target.value}"
            )

        order.status = target.value
        order.updated_at = datetime.utcnow()

        if target == OrderStatus.COMPLETED:
            order.completed_at = datetime.utcnow()
            # 释放座位
            seat_result = await self.db.execute(
                select(Seat).where(Seat.id == order.seat_id)
            )
            seat = seat_result.scalar_one_or_none()
            if seat:
                seat.status = "vacant"

        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def reject_order(
        self, order_id: str, reason: str, item_ids: Optional[list] = None
    ) -> Order:
        """拒单：全部或部分"""
        order = await self.get_order_or_404(order_id)
        order.status = OrderStatus.REJECTED.value
        order.rejected_reason = reason
        order.updated_at = datetime.utcnow()

        if item_ids:
            # 部分拒单：只标记指定items
            for oi in order.items:
                if str(oi.item_id) in item_ids:
                    # 恢复库存
                    item_result = await self.db.execute(
                        select(Item).where(Item.id == oi.item_id)
                    )
                    item = item_result.scalar_one_or_none()
                    if item and item.stock is not None:
                        item.stock += oi.quantity
        else:
            # 全单拒单：恢复所有items库存
            for oi in order.items:
                item_result = await self.db.execute(
                    select(Item).where(Item.id == oi.item_id)
                )
                item = item_result.scalar_one_or_none()
                if item and item.stock is not None:
                    item.stock += oi.quantity

        # 退款（如果已支付）
        if order.payment_status == PaymentStatus.PAID.value and order.payment_intent_id:
            from app.core.payment_service import PaymentService

            ps = PaymentService()
            ps.create_refund(order.payment_intent_id)

        # 释放座位
        seat_result = await self.db.execute(
            select(Seat).where(Seat.id == order.seat_id)
        )
        seat = seat_result.scalar_one_or_none()
        if seat:
            seat.status = "vacant"

        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def cancel_order(self, order_id: str, reason: Optional[str] = None) -> Order:
        """顾客取消：仅 submitted 状态可取消"""
        order = await self.get_order_or_404(order_id)
        if order.status != OrderStatus.SUBMITTED.value:
            raise InvalidStatusTransitionError("Only submitted orders can be cancelled")
        order.status = OrderStatus.CANCELLED.value
        order.payment_status = PaymentStatus.CANCELLED.value
        order.cancelled_at = datetime.utcnow()
        order.updated_at = datetime.utcnow()

        # 释放座位
        seat_result = await self.db.execute(
            select(Seat).where(Seat.id == order.seat_id)
        )
        seat = seat_result.scalar_one_or_none()
        if seat:
            seat.status = "vacant"

        # 退款
        if order.payment_intent_id:
            from app.core.payment_service import PaymentService

            ps = PaymentService()
            ps.create_refund(order.payment_intent_id)

        await self.db.commit()
        await self.db.refresh(order)
        return order


def _is_food(category_id: uuid.UUID) -> bool:
    """简单判断是否为食品（后续可优化为查category.name）"""
    return False  # 默认全部为饮品，按print_group处理
