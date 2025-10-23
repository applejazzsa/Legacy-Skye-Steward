# app/scripts/seed_dev.py
from __future__ import annotations

import datetime as dt
import random
from typing import Any, Dict, Iterable, List

from app.db import Base, engine, SessionLocal
from app.models import Handover, Incident, SaleItem, RevenueEntry

TENANT = "legacy"
rnd = random.Random(42)

OUTLETS = ["Main", "Terrace", "Lounge"]
SEVERITIES = ["LOW", "MEDIUM", "HIGH"]
INCIDENT_STATUS = ["OPEN", "IN_PROGRESS", "RESOLVED"]
SHIFTS = ["AM", "PM"]
PERIODS = ["BREAKFAST", "LUNCH", "DINNER"]

def cents(lo: int, hi: int) -> int:
    return rnd.randint(lo, hi) * 100

def today(delta_days: int = 0) -> dt.date:
    return (dt.datetime.now().date() + dt.timedelta(days=delta_days))

def now_minus(mins: int) -> dt.datetime:
    return dt.datetime.now() - dt.timedelta(minutes=mins)

def mcols(model) -> set[str]:
    return set(model.__table__.columns.keys())

def pick(d: Dict[str, Any], allowed: Iterable[str]) -> Dict[str, Any]:
    allowed_set = set(allowed)
    return {k: v for k, v in d.items() if k in allowed_set}

def ensure_schema_fresh() -> None:
    # Drop & recreate tables to avoid “index already exists” and stale schemas
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def seed_handovers(db) -> None:
    cols = mcols(Handover)
    rows: List[Handover] = []
    top_sales_all = ["Ribeye", "Margherita", "Sea Bass", "Truffle Pasta", "IPA", "Merlot"]

    for d in range(-3, 1):
        for shift in (SHIFTS if "shift" in cols else ["AM"]):
            payload = {
                # always safe fields
                "tenant_id": TENANT,
                "outlet": rnd.choice(OUTLETS),
                "date": today(d),

                # optional fields – we only include them if they exist on your model
                "shift": shift,
                "period": rnd.choice(PERIODS),
                "bookings": rnd.randint(10, 40),
                "walk_ins": rnd.randint(5, 30),
                "covers": rnd.randint(30, 120),
                "food_revenue": cents(300, 1600),
                "beverage_revenue": cents(150, 900),
                "top_sales": ", ".join(rnd.sample(top_sales_all, k=3)),
                "created_at": now_minus(rnd.randint(60, 360)),
            }
            rows.append(Handover(**pick(payload, cols)))
    db.add_all(rows)

def seed_incidents(db) -> None:
    cols = mcols(Incident)
    titles = [
        "POS terminal froze", "Short on glassware", "Oven preheat slow",
        "Spill at entrance", "Supplier late delivery", "Card reader intermittent",
    ]
    rows: List[Incident] = []
    for _ in range(8):
        payload = {
            "tenant_id": TENANT,
            "outlet": rnd.choice(OUTLETS),
            "severity": rnd.choice(SEVERITIES),
            "title": rnd.choice(titles),
            "status": rnd.choice(INCIDENT_STATUS),
            "created_at": now_minus(rnd.randint(30, 720)),
        }
        rows.append(Incident(**pick(payload, cols)))
    db.add_all(rows)

def seed_sale_items(db) -> None:
    """
    Handles either schema variant:
    - name/category/units_sold/revenue_cents/(sold_on optional)
    - name/qty (NOT NULL)/sold_on (NOT NULL)
    """
    cols = mcols(SaleItem)
    base = [
        ("Ribeye", "FOOD"),
        ("Margherita", "FOOD"),
        ("Sea Bass", "FOOD"),
        ("Truffle Pasta", "FOOD"),
        ("IPA", "BEVERAGE"),
        ("Merlot", "BEVERAGE"),
    ]
    rows: List[SaleItem] = []

    for i, (name, category) in enumerate(base, start=1):
        # Provide values for both styles of schema; pick() will filter.
        qty_val = rnd.randint(20, 120)
        sold_on_val = today(-rnd.randint(0, 6))  # ensure NOT NULL sold_on is satisfied
        payload = {
            "tenant_id": TENANT,
            "name": name,

            # if your table uses qty/sold_on
            "qty": qty_val,
            "sold_on": sold_on_val,

            # if your table uses these richer fields
            "category": category,
            "units_sold": qty_val,
            "revenue_cents": cents(300, 2200),

            # sometimes models include timestamps
            "created_at": now_minus(rnd.randint(10, 300)),
        }
        rows.append(SaleItem(**pick(payload, cols)))
    db.add_all(rows)

def seed_revenue_entries(db) -> None:
    cols = mcols(RevenueEntry)
    rows: List[RevenueEntry] = []
    for d in range(-6, 1):
        payload = {
            "tenant_id": TENANT,
            "outlet": rnd.choice(OUTLETS),
            "category": rnd.choice(["FOOD", "BEVERAGE"]),
            "amount_cents": cents(600, 3600),
            "occurred_at": dt.datetime.combine(today(d), dt.time(hour=rnd.choice([10, 13, 19]))),
            "description": "Auto-seeded",
        }
        rows.append(RevenueEntry(**pick(payload, cols)))
    db.add_all(rows)

def ensure_seed() -> None:
    ensure_schema_fresh()
    db = SessionLocal()
    try:
        seed_handovers(db)
        seed_incidents(db)
        seed_sale_items(db)
        seed_revenue_entries(db)
        db.commit()
        print("✅ Seeding complete for tenant:", TENANT)
    finally:
        db.close()

if __name__ == "__main__":
    ensure_seed()
