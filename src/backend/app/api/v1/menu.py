# backend/app/api/v1/menu.py
from typing import Optional

from app.database import get_db
from app.models import Category, Item
from app.schemas.menu import CategoryWithItems, ItemResponse, MenuResponse
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/menu", response_model=MenuResponse)
async def get_menu(
    lang: str = Query("zh", regex="^(zh|en)$"),
    db: AsyncSession = Depends(get_db),
):
    """返回完整菜单，按分类排序"""
    result = await db.execute(
        select(Category).where(Category.is_active == True).order_by(Category.sort_order)
    )
    categories = result.scalars().all()

    items_result = await db.execute(
        select(Item)
        .where(Item.is_active == True, Item.is_available == True)
        .order_by(Item.sort_order)
    )
    all_items = items_result.scalars().all()

    # 按 category_id 分组
    from collections import defaultdict

    items_by_cat = defaultdict(list)
    for it in all_items:
        items_by_cat[str(it.category_id)].append(it)

    cats_out = []
    for cat in categories:
        name = cat.name_zh if lang == "zh" else cat.name_en
        items_out = []
        for it in items_by_cat.get(str(cat.id), []):
            item_data = {
                "id": str(it.id),
                "name_zh": it.name_zh,
                "name_en": it.name_en,
                "description_zh": it.description_zh,
                "description_en": it.description_en,
                "price_sgd": float(it.price_sgd),
                "image_url": it.image_url,
                "options_config": it.options_config or {},
                "is_available": it.is_available,
            }
            items_out.append(ItemResponse(**item_data))
        cats_out.append(
            CategoryWithItems(
                id=str(cat.id),
                name=name,
                sort_order=cat.sort_order,
                items=items_out,
            )
        )

    return MenuResponse(categories=cats_out)


@router.get("/menu/items/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: str,
    lang: str = Query("zh", regex="^(zh|en)$"),
    db: AsyncSession = Depends(get_db),
):
    """返回单个商品详情"""
    import uuid

    try:
        uid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    result = await db.execute(select(Item).where(Item.id == uid))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return ItemResponse(
        id=str(item.id),
        name_zh=item.name_zh,
        name_en=item.name_en,
        description_zh=item.description_zh,
        description_en=item.description_en,
        price_sgd=float(item.price_sgd),
        image_url=item.image_url,
        options_config=item.options_config or {},
        is_available=item.is_available,
    )
