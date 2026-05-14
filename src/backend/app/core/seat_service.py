# backend/app/core/seat_service.py
from typing import Optional

from app.models import Seat
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class SeatNotFoundError(Exception):
    pass


class SeatService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_seats(self, include_inactive: bool = False):
        query = select(Seat)
        if not include_inactive:
            query = query.where(Seat.is_active == True)
        query = query.order_by(Seat.zone, Seat.id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_seat(self, seat_id: str) -> Optional[Seat]:
        result = await self.db.execute(select(Seat).where(Seat.id == seat_id))
        return result.scalar_one_or_none()

    async def get_seat_or_404(self, seat_id: str) -> Seat:
        seat = await self.get_seat(seat_id)
        if not seat:
            raise SeatNotFoundError(f"Seat {seat_id} not found")
        return seat

    async def update_status(self, seat_id: str, status: str) -> Seat:
        valid = {"vacant", "occupied", "reserved", "inactive"}
        if status not in valid:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid}")
        seat = await self.get_seat_or_404(seat_id)
        seat.status = status
        from datetime import datetime

        seat.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(seat)
        return seat
