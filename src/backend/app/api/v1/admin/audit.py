# backend/app/api/v1/admin/audit.py
"""Admin audit log endpoints."""
from datetime import datetime

from app.core.auth_service import get_current_admin
from app.database import get_db
from app.models import AdminAuditLog
from app.models.admin_user import AdminUser
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class AuditLogResponse(BaseModel):
    id: str
    admin_user_id: str
    admin_email: str
    action: str
    target_type: str
    target_id: str
    old_value: dict | None
    new_value: dict | None
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    logs: list[AuditLogResponse]
    total_count: int


@router.get("/", response_model=AuditLogListResponse)
async def list_audit_logs(
    target_type: str = Query(
        None, description="Filter by target type (item, category, seat, order)"
    ),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """List admin audit logs, most recent first."""
    # Count
    from sqlalchemy import func

    count_query = select(func.count(AdminAuditLog.id))
    if target_type:
        count_query = count_query.where(AdminAuditLog.target_type == target_type)
    total = (await db.execute(count_query)).scalar() or 0

    # Fetch page
    offset = (page - 1) * limit
    query = (
        select(AdminAuditLog)
        .order_by(AdminAuditLog.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    if target_type:
        query = query.where(AdminAuditLog.target_type == target_type)

    result = await db.execute(query)
    logs = result.scalars().all()

    return AuditLogListResponse(
        logs=[
            AuditLogResponse(
                id=str(log.id),
                admin_user_id=str(log.admin_user_id),
                admin_email=log.admin_user.email if log.admin_user else "Unknown",
                action=log.action,
                target_type=log.target_type,
                target_id=log.target_id,
                old_value=log.old_value,
                new_value=log.new_value,
                created_at=log.created_at,
            )
            for log in logs
        ],
        total_count=total,
    )
