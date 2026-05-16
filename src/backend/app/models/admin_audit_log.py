# backend/app/models/admin_audit_log.py
import uuid
from datetime import datetime

from app.models.base import Base
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship


class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    admin_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("admin_users.id"), nullable=False
    )
    action: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # create, update, delete
    target_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # item, category, seat, order
    target_id: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    new_value: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    admin_user: Mapped["AdminUser"] = relationship("AdminUser", lazy="selectin")
