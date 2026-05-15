# backend/app/api/v1/admin/items.py
"""Admin CRUD endpoints for menu items."""
import uuid
from datetime import datetime
from decimal import Decimal

from app.core.auth_service import get_current_admin
from app.database import get_db
from app.models import Category, Item
from app.models.admin_user import AdminUser
from app.schemas.admin import ItemAdminResponse, ItemCreateRequest, ItemUpdateRequest
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def _to_response(item: Item) -> ItemAdminResponse:
    return ItemAdminResponse(
        id=str(item.id),
        category_id=str(item.category_id),
        name_zh=item.name_zh,
        name_en=item.name_en,
        description_zh=item.description_zh,
        description_en=item.description_en,
        price_sgd=float(item.price_sgd),
        image_url=item.image_url,
        options_config=item.options_config or {},
        is_available=item.is_available,
        stock=item.stock,
        sort_order=item.sort_order,
        is_active=item.is_active,
    )


@router.get("/", response_model=list[ItemAdminResponse])
async def list_items(
    category_id: str = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """List all items (including inactive/unavailable) for admin management."""
    query = select(Item).order_by(Item.sort_order)
    if category_id:
        try:
            cat_uid = uuid.UUID(category_id)
            query = query.where(Item.category_id == cat_uid)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid category ID")
    result = await db.execute(query)
    return [_to_response(i) for i in result.scalars().all()]


@router.post("/", response_model=ItemAdminResponse, status_code=201)
async def create_item(
    data: ItemCreateRequest,
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Create a new menu item."""
    # Validate category exists
    try:
        cat_uid = uuid.UUID(data.category_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid category ID")

    cat_result = await db.execute(select(Category).where(Category.id == cat_uid))
    if not cat_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Category not found")

    item = Item(
        category_id=cat_uid,
        name_zh=data.name_zh,
        name_en=data.name_en,
        description_zh=data.description_zh,
        description_en=data.description_en,
        price_sgd=Decimal(str(data.price_sgd)),
        image_url=data.image_url,
        options_config=data.options_config,
        is_available=data.is_available,
        stock=data.stock,
        sort_order=data.sort_order,
        is_active=data.is_active,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return _to_response(item)


@router.put("/{item_id}", response_model=ItemAdminResponse)
async def update_item(
    item_id: str,
    data: ItemUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Update an existing menu item."""
    try:
        uid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID")

    result = await db.execute(select(Item).where(Item.id == uid))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = data.model_dump(exclude_unset=True)

    # Validate category if being changed
    if "category_id" in update_data:
        try:
            cat_uid = uuid.UUID(update_data["category_id"])
            update_data["category_id"] = cat_uid
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid category ID")
        cat_result = await db.execute(select(Category).where(Category.id == cat_uid))
        if not cat_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Category not found")

    # Convert price to Decimal
    if "price_sgd" in update_data:
        update_data["price_sgd"] = Decimal(str(update_data["price_sgd"]))

    for field, value in update_data.items():
        setattr(item, field, value)
    item.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(item)
    return _to_response(item)


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Soft-delete an item by setting is_active=False."""
    try:
        uid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID")

    result = await db.execute(select(Item).where(Item.id == uid))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.is_active = False
    item.updated_at = datetime.utcnow()
    await db.commit()
