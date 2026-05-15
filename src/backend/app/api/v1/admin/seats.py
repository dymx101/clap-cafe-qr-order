# backend/app/api/v1/admin/seats.py
"""Admin CRUD endpoints for seats."""
from datetime import datetime

from app.core.auth_service import get_current_admin
from app.database import get_db
from app.models import Seat
from app.models.admin_user import AdminUser
from app.schemas.admin import SeatCreateRequest, SeatUpdateRequest
from app.schemas.seat import SeatResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def _to_response(seat: Seat) -> SeatResponse:
    return SeatResponse(
        id=seat.id,
        label_zh=seat.label_zh,
        label_en=seat.label_en,
        zone=seat.zone,
        status=seat.status,
        is_active=seat.is_active,
    )


@router.get("/", response_model=list[SeatResponse])
async def list_seats(
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """List all seats (including inactive) for admin management."""
    result = await db.execute(select(Seat).order_by(Seat.zone, Seat.id))
    return [_to_response(s) for s in result.scalars().all()]


@router.post("/", response_model=SeatResponse, status_code=201)
async def create_seat(
    data: SeatCreateRequest,
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Create a new seat."""
    # Check if seat ID already exists
    existing = await db.execute(select(Seat).where(Seat.id == data.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Seat '{data.id}' already exists")

    seat = Seat(
        id=data.id,
        label_zh=data.label_zh,
        label_en=data.label_en,
        zone=data.zone,
        status=data.status,
        is_active=data.is_active,
    )
    db.add(seat)
    await db.commit()
    await db.refresh(seat)
    return _to_response(seat)


@router.put("/{seat_id}", response_model=SeatResponse)
async def update_seat(
    seat_id: str,
    data: SeatUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Update an existing seat."""
    result = await db.execute(select(Seat).where(Seat.id == seat_id))
    seat = result.scalar_one_or_none()
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")

    update_data = data.model_dump(exclude_unset=True)

    # Validate status if provided
    if "status" in update_data:
        valid = {"vacant", "occupied", "reserved", "inactive"}
        if update_data["status"] not in valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of {valid}",
            )

    for field, value in update_data.items():
        setattr(seat, field, value)
    seat.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(seat)
    return _to_response(seat)


@router.delete("/{seat_id}", status_code=204)
async def delete_seat(
    seat_id: str,
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    """Soft-delete a seat by setting is_active=False."""
    result = await db.execute(select(Seat).where(Seat.id == seat_id))
    seat = result.scalar_one_or_none()
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")

    seat.is_active = False
    seat.updated_at = datetime.utcnow()
    await db.commit()
