# scripts/seed_demo.py
# Robust path bootstrap so we can import "app" regardless of how this file is called.
import os
import sys
from datetime import datetime, timedelta, time, timezone
from sqlalchemy.orm import Session

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.db import SessionLocal, engine, Base
from app import models


def dt_at(d, hh, mm, ss=0):
    """Create a timezone-aware UTC datetime for date d at hh:mm:ss."""
    return datetime.combine(d, time(hh, mm, ss, tzinfo=timezone.utc))


def seed():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        # Clear existing data (demo only)
        db.query(models.GuestNote).delete()
        db.query(models.Incident).delete()
        db.query(models.Handover).delete()
        db.commit()

        today = datetime.now(timezone.utc).date()
        days = [today - timedelta(days=i) for i in range(6, -1, -1)]  # last 7 days (Mon-Sun style window)

        outlets = ["Cafe Grill", "Leopard Bar", "Azure", "Spa"]
        periods = [
            models.MealPeriodEnum.BREAKFAST,
            models.MealPeriodEnum.LUNCH,
            models.MealPeriodEnum.DINNER,
        ]

        # ---------------------------
        # Handovers (7 days × 4 outlets × 3 periods)
        # ---------------------------
        for d in days:
            for out in outlets:
                for p in periods:
                    shift = (
                        models.ShiftEnum.AM if p == models.MealPeriodEnum.BREAKFAST
                        else models.ShiftEnum.PM if p == models.MealPeriodEnum.DINNER
                        else (models.ShiftEnum.AM if (d.day + len(out)) % 2 == 0 else models.ShiftEnum.PM)
                    )
                    hov = models.Handover(
                        outlet=out,
                        date=dt_at(d, 9, 0) if shift == models.ShiftEnum.AM else dt_at(d, 18, 0),
                        shift=shift,
                        period=p,
                        bookings=10 + (d.day % 5),
                        walk_ins=5 + (len(out) % 4),
                        covers=25 + (d.day % 10),
                        food_revenue=8000 + (d.day % 7) * 900,
                        beverage_revenue=600 + (d.day % 6) * 120,
                        top_sales_csv="Beef Fillet,Atlantic Platter" if out != "Spa" else ""
                    )
                    db.add(hov)

        # ---------------------------
        # Incidents (use timedelta, not day-1)
        # ---------------------------
        inc_today = today
        inc_yesterday = today - timedelta(days=1)

        db.add_all([
            models.Incident(
                outlet="Azure",
                date=dt_at(inc_today, 20, 15),
                description="Child choked due to unblended veg; assisted promptly.",
                severity=models.SeverityEnum.HIGH,
                owner="Duty Manager",
                status=models.IncidentStatusEnum.OPEN,
                guest_reference="Room 209"
            ),
            models.Incident(
                outlet="Leopard Bar",
                date=dt_at(inc_yesterday, 16, 45),
                description="Scones slightly stale; replaced immediately and comped tea.",
                severity=models.SeverityEnum.MEDIUM,
                owner="F&B Supervisor",
                status=models.IncidentStatusEnum.RESOLVED,
                action_taken="Replaced; QA check on batch."
            ),
        ])

        # ---------------------------
        # Guest notes (also timedelta-safe)
        # ---------------------------
        db.add_all([
            models.GuestNote(
                outlet="Leopard Bar",
                date=dt_at(inc_today, 15, 30),
                guest_name="Private",
                occasion="Anniversary",
                note="Loved High Tea and cocktails; praised Nolundi.",
                sentiment=models.SentimentEnum.VERY_HAPPY,
                staff_praised="Nolundi"
            ),
            models.GuestNote(
                outlet="Spa",
                date=dt_at(today - timedelta(days=2), 11, 0),
                guest_name=None,
                note="Complimented Jade’s healing hands.",
                sentiment=models.SentimentEnum.HAPPY,
                staff_praised="Jade"
            ),
        ])

        db.commit()
        print("✅ Demo data seeded.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
