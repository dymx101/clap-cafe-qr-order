# backend/app/api/v1/admin/categories.py
"""Admin CRUD endpoints for menu categories."""
import uuid
from datetime import datetime

from app.core.audit_service import log_admin_action
from app.core.auth_service import get_current_admin
from app.database import get_db
from app.models import Category
from app.models.admin_user import AdminUser
from app.schemas.admin import (
    CategoryAdminResponse,
    CategoryCreateRequest,
    CategoryUpdateRequest,
)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def _to_response(cat: Category) -> CategoryAdminResponse:
    return CategoryAdminResponse(
        id=str(cat.id),
        name_zh=cat.name_zh,
        name_en=cat.name_en,
        sort_order=cat.sort_order,
        is_active=cat.is_active,
    )


@router.get("/", response_model=list[CategoryAdminResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """List all categories (including inactive) for admin management."""
    result = await db.execute(select(Category).order_by(Category.sort_order))
    return [_to_response(c) for c in result.scalars().all()]


@router.post("/", response_model=CategoryAdminResponse, status_code=201)
async def create_category(
    data: CategoryCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """Create a new menu category."""
    cat = Category(
        name_zh=data.name_zh,
        name_en=data.name_en,
        sort_order=data.sort_order,
        is_active=data.is_active,
    )
    db.add(cat)
    await db.commit()
    await db.refresh(cat)

    await log_admin_action(
        db,
        admin.id,
        "create",
        "category",
        str(cat.id),
        new_value={"name_en": cat.name_en, "name_zh": cat.name_zh},
    )

    return _to_response(cat)


@router.put("/{category_id}", response_model=CategoryAdminResponse)
async def update_category(
    category_id: str,
    data: CategoryUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """Update an existing category."""
    try:
        uid = uuid.UUID(category_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid category ID")

    result = await db.execute(select(Category).where(Category.id == uid))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    old_values = {}
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        old_values[field] = getattr(cat, field)
        setattr(cat, field, value)
    cat.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(cat)

    await log_admin_action(
        db,
        admin.id,
        "update",
        "category",
        str(cat.id),
        old_value=old_values,
        new_value=update_data,
    )

    return _to_response(cat)


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin),
):
    """Soft-delete a category by setting is_active=False."""
    try:
        uid = uuid.UUID(category_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid category ID")

    result = await db.execute(select(Category).where(Category.id == uid))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")

    cat.is_active = False
    cat.updated_at = datetime.utcnow()
    await db.commit()

    await log_admin_action(
        db, admin.id, "delete", "category", str(cat.id), old_value={"is_active": True}
    )
