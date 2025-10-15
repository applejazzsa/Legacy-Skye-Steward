from __future__ import annotations
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db import get_session
from app.models import Handover, GuestNote

def seed(db: Session) -> None:
    now = datetime.utcnow()

    handovers = [
        Handover(
            outlet="Main Restaurant",
            date=now - timedelta(days=2),
            shift="AM",
            period="BREAKFAST",
            bookings=12, walk_ins=6, covers=34,
            food_revenue=800.00, beverage_revenue=210.00,
            top_sales=["Pancakes", "Omelette", "Latte"],
        ),
        Handover(
            outlet="Main Restaurant",
            date=now - timedelta(days=1),
            shift="PM",
            period="DINNER",
            bookings=25, walk_ins=18, covers=92,
            food_revenue=3400.50, beverage_revenue=1280.25,
            top_sales=["Ribeye", "Sea Bass", "Cabernet"],
        ),
    ]
    notes = [
        GuestNote(guest_name="Jane Doe", note="Prefers window seating; lactose-free."),
        GuestNote(guest_name="John Smith", note="Anniversary celebration; enjoys Cabernet."),
    ]

    db.add_all(handovers + notes)
    db.commit()

if __name__ == "__main__":
    with get_session() as db:
        seed(db)
    print("Seeded demo rows.")
