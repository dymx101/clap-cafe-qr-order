# backend/app/models/order.py
import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.models.base import Base
from sqlalchemy import CheckConstraint, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OrderStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


ORDER_STATUS_TRANSITIONS = {
    OrderStatus.SUBMITTED: {
        OrderStatus.CONFIRMED,
        OrderStatus.REJECTED,
        OrderStatus.CANCELLED,
    },
    OrderStatus.CONFIRMED: {OrderStatus.PREPARING, OrderStatus.CANCELLED},
    OrderStatus.PREPARING: {OrderStatus.READY, OrderStatus.CANCELLED},
    OrderStatus.READY: {OrderStatus.COMPLETED},
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELLED: set(),
    OrderStatus.REJECTED: set(),
}


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint(
            "status IN ('submitted','confirmed','preparing','ready','completed','cancelled','rejected')",
            name="ck_orders_status",
        ),
        CheckConstraint(
            "payment_status IN ('pending','paid','failed','refunded','cancelled')",
            name="ck_orders_payment_status",
        ),
    )

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    seat_id: Mapped[str] = mapped_column(
        String(10), ForeignKey("seats.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=OrderStatus.SUBMITTED.value
    )
    payment_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=PaymentStatus.PENDING.value
    )
    payment_method: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    payment_intent_id: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    subtotal_sgd: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    tax_sgd: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_sgd: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    customer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rejected_reason: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    paid_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    seat: Mapped["Seat"] = relationship("Seat", lazy="selectin")
