# backend/app/api/v1/seat.py
from app.core.seat_service import SeatNotFoundError, SeatService
from app.database import get_db
from app.schemas.seat import SeatListResponse, SeatResponse, SeatStatusUpdate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/seats", response_model=SeatListResponse)
async def list_seats(db: AsyncSession = Depends(get_db)):
    svc = SeatService(db)
    seats = await svc.list_seats()
    return SeatListResponse(
        seats=[
            SeatResponse(
                id=s.id,
                label_zh=s.label_zh,
                label_en=s.label_en,
                zone=s.zone,
                status=s.status,
                is_active=s.is_active,
            )
            for s in seats
        ]
    )


@router.get("/seats/{seat_id}", response_model=SeatResponse)
async def get_seat(seat_id: str, db: AsyncSession = Depends(get_db)):
    svc = SeatService(db)
    try:
        seat = await svc.get_seat_or_404(seat_id)
        return SeatResponse(
            id=seat.id,
            label_zh=seat.label_zh,
            label_en=seat.label_en,
            zone=seat.zone,
            status=seat.status,
            is_active=seat.is_active,
        )
    except SeatNotFoundError:
        raise HTTPException(status_code=404, detail="Seat not found")


@router.put("/seats/{seat_id}/status", response_model=SeatResponse)
async def update_seat_status(
    seat_id: str,
    data: SeatStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    svc = SeatService(db)
    try:
        seat = await svc.update_status(seat_id, data.status)
        return SeatResponse(
            id=seat.id,
            label_zh=seat.label_zh,
            label_en=seat.label_en,
            zone=seat.zone,
            status=seat.status,
            is_active=seat.is_active,
        )
    except SeatNotFoundError:
        raise HTTPException(status_code=404, detail="Seat not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
