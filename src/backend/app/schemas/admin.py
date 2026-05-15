# backend/app/schemas/admin.py
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# --- Auth ---
class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin: "AdminUserResponse"


# --- Admin User ---
class AdminUserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


# --- Category CRUD ---
class CategoryCreateRequest(BaseModel):
    name_zh: str = Field(max_length=100)
    name_en: str = Field(max_length=100)
    sort_order: int = 0
    is_active: bool = True


class CategoryUpdateRequest(BaseModel):
    name_zh: Optional[str] = Field(None, max_length=100)
    name_en: Optional[str] = Field(None, max_length=100)
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryAdminResponse(BaseModel):
    id: str
    name_zh: str
    name_en: str
    sort_order: int
    is_active: bool

    class Config:
        from_attributes = True


# --- Item CRUD ---
class ItemCreateRequest(BaseModel):
    category_id: str
    name_zh: str = Field(max_length=200)
    name_en: str = Field(max_length=200)
    description_zh: Optional[str] = None
    description_en: Optional[str] = None
    price_sgd: float = Field(gt=0)
    image_url: Optional[str] = None
    options_config: dict = Field(default_factory=dict)
    is_available: bool = True
    stock: Optional[int] = None
    sort_order: int = 0
    is_active: bool = True


class ItemUpdateRequest(BaseModel):
    category_id: Optional[str] = None
    name_zh: Optional[str] = Field(None, max_length=200)
    name_en: Optional[str] = Field(None, max_length=200)
    description_zh: Optional[str] = None
    description_en: Optional[str] = None
    price_sgd: Optional[float] = Field(None, gt=0)
    image_url: Optional[str] = None
    options_config: Optional[dict] = None
    is_available: Optional[bool] = None
    stock: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class ItemAdminResponse(BaseModel):
    id: str
    category_id: str
    name_zh: str
    name_en: str
    description_zh: Optional[str] = None
    description_en: Optional[str] = None
    price_sgd: float
    image_url: Optional[str] = None
    options_config: dict = Field(default_factory=dict)
    is_available: bool
    stock: Optional[int] = None
    sort_order: int
    is_active: bool

    class Config:
        from_attributes = True


# --- Seat CRUD ---
class SeatCreateRequest(BaseModel):
    id: str = Field(max_length=10)
    label_zh: str = Field(max_length=50)
    label_en: str = Field(max_length=50)
    zone: str = Field(max_length=20)
    status: str = "vacant"
    is_active: bool = True


class SeatUpdateRequest(BaseModel):
    label_zh: Optional[str] = Field(None, max_length=50)
    label_en: Optional[str] = Field(None, max_length=50)
    zone: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = None
    is_active: Optional[bool] = None
