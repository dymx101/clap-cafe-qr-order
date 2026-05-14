# backend/app/scripts/init_seats.py
"""初始化座位数据"""
import asyncio

from app.database import AsyncSessionLocal
from app.models import Seat

SEATS_DATA = [
    # Indoor T01-T12
    *[
        {
            "id": f"T{i:02d}",
            "label_zh": f"{i}号桌",
            "label_en": f"Table {i:02d}",
            "zone": "indoor",
        }
        for i in range(1, 13)
    ],
    # Outdoor O01-O04
    *[
        {
            "id": f"O{i:02d}",
            "label_zh": f"户外{i}号桌",
            "label_en": f"Outdoor {i:02d}",
            "zone": "outdoor",
        }
        for i in range(1, 5)
    ],
    # Bar B01-B06
    *[
        {
            "id": f"B{i:02d}",
            "label_zh": f"吧台{i}号座",
            "label_en": f"Bar Seat {i:02d}",
            "zone": "bar",
        }
        for i in range(1, 7)
    ],
]


async def main():
    async with AsyncSessionLocal() as db:
        for data in SEATS_DATA:
            existing = await db.get(Seat, data["id"])
            if not existing:
                seat = Seat(**data, status="vacant", is_active=True)
                db.add(seat)
        await db.commit()
        print(f"Initialized {len(SEATS_DATA)} seats")


if __name__ == "__main__":
    asyncio.run(main())
