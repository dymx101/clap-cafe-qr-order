# backend/app/schemas/seat.py
from typing import Optional

from pydantic import BaseModel


class SeatResponse(BaseModel):
    id: str
    label_zh: str
    label_en: str
    zone: str
    status: str
    is_active: bool

    class Config:
        from_attributes = True


class SeatStatusUpdate(BaseModel):
    status: str


class SeatListResponse(BaseModel):
    seats: list[SeatResponse]
