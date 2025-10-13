"""Seed the database with demo data."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from random import randint

from sqlalchemy.orm import Session

from app.db import Base, engine, get_session
from app.models import GuestNote, Handover


def ensure_schema() -> None:
    """Create tables if they are missing."""

    Base.metadata.create_all(bind=engine)


def seed_handovers(session: Session) -> None:
    now = datetime.now(timezone.utc)
    outlets = ["Main Restaurant", "Lobby Bar"]

    demo_records: list[Handover] = []
    for day_offset in range(3, 0, -1):
        for outlet in outlets:
            base_date = now - timedelta(days=day_offset)
            shift = "AM" if outlet == "Main Restaurant" else "PM"
            period = "BREAKFAST" if shift == "AM" else "DINNER"
            handover = Handover(
                outlet=outlet,
                date=base_date.replace(
                    hour=8 if shift == "AM" else 19,
                    minute=0,
                    second=0,
                    microsecond=0,
                ),
                shift=shift,
                period=period,
                bookings=randint(10, 40),
                walk_ins=randint(5, 25),
                covers=randint(40, 120),
                food_revenue=round(randint(2000, 8000) + randint(0, 99) / 100, 2),
                beverage_revenue=round(randint(800, 3500) + randint(0, 99) / 100, 2),
                top_sales=[
                    "Chef's Special",
                    "Signature Cocktail" if outlet == "Lobby Bar" else "Tasting Menu",
                    "Seasonal Dessert",
                ],
            )
            demo_records.append(handover)
    session.add_all(demo_records)


def seed_guest_notes(session: Session) -> None:
    base_time = datetime.now(timezone.utc) - timedelta(days=1)
    notes = [
        GuestNote(
            date=base_time - timedelta(hours=6),
            staff="Alex Kim",
            note="Guests praised attentive wine pairing recommendations.",
            outlet="Main Restaurant",
        ),
        GuestNote(
            date=base_time - timedelta(hours=3),
            staff="Jamie Rivera",
            note="Birthday party commended the cocktail flair show.",
            outlet="Lobby Bar",
        ),
        GuestNote(
            date=base_time - timedelta(hours=1),
            staff="Morgan Patel",
            note="VIP appreciated the personalized dessert inscription.",
            outlet="Main Restaurant",
        ),
    ]
    session.add_all(notes)


def main() -> None:
    ensure_schema()
    session = get_session()
    try:
        seed_handovers(session)
        seed_guest_notes(session)
        session.commit()
        print("Seed data inserted successfully.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
