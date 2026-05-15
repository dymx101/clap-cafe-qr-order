# backend/app/schemas/order.py
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    item_id: str
    quantity: int = Field(ge=1)
    options: dict = Field(default_factory=dict)
    notes: Optional[str] = None


class OrderCreate(BaseModel):
    seat_id: str
    items: List[OrderItemCreate]
    customer_notes: Optional[str] = None


class OrderItemResponse(BaseModel):
    id: str
    item_id: str
    item_name_zh: str
    item_name_en: str
    quantity: int
    unit_price: float
    options: dict
    notes: Optional[str] = None
    print_group: str

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: str
    seat_id: str
    status: str
    payment_status: str
    payment_method: Optional[str] = None
    payment_intent_id: Optional[str] = None
    items: List[OrderItemResponse] = []
    subtotal_sgd: float
    tax_sgd: float
    total_sgd: float
    notes: Optional[str] = None
    customer_notes: Optional[str] = None
    rejected_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderStatusResponse(BaseModel):
    id: str
    status: str
    payment_status: str
    updated_at: datetime


class OrderStatusUpdate(BaseModel):
    status: str


class OrderRejectRequest(BaseModel):
    reason: str
    items: Optional[List[str]] = None  # UUIDs of order_items; if None, reject all


class OrderCancelRequest(BaseModel):
    reason: Optional[str] = None
