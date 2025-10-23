# app/scripts/seed_dev.py
from datetime import date, timedelta
import random
from sqlalchemy.orm import Session

from ..db import engine, SessionLocal, Base
from ..models import Handover, SaleItem, Incident

TENANT = "legacy"

def rnd(a, b):  # inclusive
    return random.randint(a, b)

def seed_handover(db: Session, start: date, days: int):
    rows = []
    for i in range(days):
        d = start + timedelta(days=i)
        for outlet in ["Main", "Lounge", "Terrace"]:
            covers = rnd(40, 120)
            food = rnd(1200, 4200)
            bev = rnd(800, 2600)
            rows.append(
                Handover(
                    tenant_id=TENANT,
                    outlet=outlet,
                    date=d,
                    shift="PM" if rnd(0, 1) else "AM",
                    covers=covers,
                    food_revenue=float(food),
                    beverage_revenue=float(bev),
                    top_sales=None,
                )
            )
    db.add_all(rows)

def seed_sales(db: Session, start: date, days: int):
    items = ["Ribeye", "Margherita", "Truffle Pasta", "IPA", "Sea Bass", "Caesar", "Coke"]
    rows = []
    for i in range(days):
        sold_on = start + timedelta(days=i)
        for name in items:
            rows.append(
                SaleItem(
                    tenant_id=TENANT,
                    name=name,
                    qty=rnd(20, 140),
                    sold_on=sold_on,
                )
            )
    db.add_all(rows)

def seed_incidents(db: Session, start: date):
    rows = [
        Incident(
            tenant_id=TENANT,
            outlet="Main",
            severity="LOW",
            title="Cutlery shortage",
            status="OPEN",
            created_at=start,
        ),
        Incident(
            tenant_id=TENANT,
            outlet="Lounge",
            severity="MEDIUM",
            title="POS intermittently offline",
            status="IN_PROGRESS",
            created_at=start + timedelta(days=1),
        ),
    ]
    db.add_all(rows)

def ensure_seed():
    # start clean
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        start = date.today() - timedelta(days=29)  # last 30 days
        seed_handover(db, start, 30)
        seed_sales(db, start, 30)
        seed_incidents(db, start)
        db.commit()
        print("Seeded.")
    finally:
        db.close()

if __name__ == "__main__":
    ensure_seed()
