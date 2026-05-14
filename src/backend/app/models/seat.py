# backend/app/models/seat.py
from datetime import datetime

from app.models.base import Base
from sqlalchemy import Boolean, CheckConstraint, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


class Seat(Base):
    __tablename__ = "seats"
    __table_args__ = (
        CheckConstraint(
            "status IN ('vacant','occupied','reserved','inactive')",
            name="ck_seats_status",
        ),
    )

    id: Mapped[str] = mapped_column(String(10), primary_key=True)
    label_zh: Mapped[str] = mapped_column(String(50), nullable=False)
    label_en: Mapped[str] = mapped_column(String(50), nullable=False)
    zone: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="vacant")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
