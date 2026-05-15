# backend/app/schemas/menu.py
from typing import List, Optional

from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    id: str
    category_id: str
    name_zh: str
    name_en: str
    description_zh: Optional[str] = None
    description_en: Optional[str] = None
    price_sgd: float
    image_url: Optional[str] = None
    options_config: dict = Field(default_factory=dict)
    is_available: bool = True
    stock: Optional[int] = None
    sort_order: int = 0


class ItemResponse(ItemBase):
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    id: str
    name_zh: str
    name_en: str
    sort_order: int


class CategoryWithItems(CategoryBase):
    items: List[ItemResponse] = []


class MenuResponse(BaseModel):
    categories: List[CategoryWithItems] = []
