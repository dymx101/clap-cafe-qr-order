# backend/app/core/audit_service.py
import uuid
from datetime import datetime

from app.models import AdminAuditLog
from sqlalchemy.ext.asyncio import AsyncSession


async def log_admin_action(
    db: AsyncSession,
    admin_user_id: uuid.UUID,
    action: str,
    target_type: str,
    target_id: str,
    old_value: dict | None = None,
    new_value: dict | None = None,
) -> None:
    """Record an admin action in the audit log."""
    log = AdminAuditLog(
        admin_user_id=admin_user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        old_value=old_value,
        new_value=new_value,
    )
    db.add(log)
    await db.commit()
