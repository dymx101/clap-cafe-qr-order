# backend/app/models/payment.py
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.models.base import Base
from sqlalchemy import DateTime, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    order_id: Mapped[str] = mapped_column(String(20), nullable=False)
    stripe_payment_intent: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True
    )
    paynow_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    amount_sgd: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="SGD")
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    payment_method: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    failure_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    failure_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
