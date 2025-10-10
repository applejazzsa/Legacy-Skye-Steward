from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db import SessionLocal, engine, Base
from app import models

def seed():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        # Clear existing (demo only)
        db.query(models.GuestNote).delete()
        db.query(models.Incident).delete()
        db.query(models.Handover).delete()
        db.commit()

        today = datetime.utcnow().date()
        days = [today - timedelta(days=i) for i in range(6, -1, -1)]  # last 7 days

        outlets = ["Cafe Grill", "Leopard Bar", "Azure", "Spa"]
        periods = [models.MealPeriodEnum.BREAKFAST, models.MealPeriodEnum.LUNCH, models.MealPeriodEnum.DINNER]
        shifts = [models.ShiftEnum.AM, models.ShiftEnum.PM]

        # Handovers
        for d in days:
            for out in outlets:
                for p in periods:
                    # pick AM for breakfast, PM for dinner; lunch random
                    sh = models.ShiftEnum.AM if p == models.MealPeriodEnum.BREAKFAST else (models.ShiftEnum.PM if p == models.MealPeriodEnum.DINNER else shifts[(d.day + len(out)) % 2])
                    hov = models.Handover(
                        outlet=out,
                        date=datetime(d.year, d.month, d.day, 9 if sh == models.ShiftEnum.AM else 18, 0, 0),
                        shift=sh,
                        period=p,
                        bookings=10 + (d.day % 5),
                        walk_ins=5 + (len(out) % 4),
                        covers=25 + (d.day % 10),
                        food_revenue=8000 + (d.day % 7) * 900,
                        beverage_revenue=600 + (d.day % 6) * 120,
                        top_sales_csv="Beef Fillet,Atlantic Platter" if out != "Spa" else ""
                    )
                    db.add(hov)

        # Incidents
        db.add_all([
            models.Incident(
                outlet="Azure",
                date=datetime(today.year, today.month, today.day, 20, 15, 0),
                description="Child choked due to unblended veg; assisted promptly.",
                severity=models.SeverityEnum.HIGH,
                owner="Duty Manager",
                status=models.IncidentStatusEnum.OPEN,
                guest_reference="Room 209"
            ),
            models.Incident(
                outlet="Leopard Bar",
                date=datetime(today.year, today.month, today.day-1, 16, 45, 0),
                description="Scones slightly stale; replaced immediately and comped tea.",
                severity=models.SeverityEnum.MEDIUM,
                owner="F&B Supervisor",
                status=models.IncidentStatusEnum.RESOLVED,
                action_taken="Replaced; QA check on batch."
            ),
        ])

        # Guest notes
        db.add_all([
            models.GuestNote(
                outlet="Leopard Bar",
                date=datetime(today.year, today.month, today.day, 15, 30, 0),
                guest_name="Private",
                occasion="Anniversary",
                note="Loved High Tea and cocktails; praised Nolundi.",
                sentiment=models.SentimentEnum.VERY_HAPPY,
                staff_praised="Nolundi"
            ),
            models.GuestNote(
                outlet="Spa",
                date=datetime(today.year, today.month, today.day-2, 11, 0, 0),
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
