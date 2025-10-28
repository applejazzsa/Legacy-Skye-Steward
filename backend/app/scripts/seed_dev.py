# app/scripts/seed_dev.py
from __future__ import annotations

import datetime as dt
import random
from typing import Any, Dict, Iterable, List

from app.db import Base, engine, SessionLocal
from app.models import (
    Handover,
    Incident,
    SaleItem,
    RevenueEntry,
    ChecklistTemplate,
    ChecklistResponse,
    Vehicle,
    VehicleBooking,
    CapaAction,
)

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
    return dt.datetime.now().date() + dt.timedelta(days=delta_days)


def now_minus(mins: int) -> dt.datetime:
    return dt.datetime.now() - dt.timedelta(minutes=mins)


def mcols(model) -> set[str]:
    return set(model.__table__.columns.keys())


def pick(d: Dict[str, Any], allowed: Iterable[str]) -> Dict[str, Any]:
    allowed_set = set(allowed)
    return {k: v for k, v in d.items() if k in allowed_set}


def ensure_schema_fresh() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed_handovers(db) -> None:
    cols = mcols(Handover)
    rows: List[Handover] = []
    top_sales_all = ["Ribeye", "Margherita", "Sea Bass", "Truffle Pasta", "IPA", "Merlot"]

    for d in range(-3, 1):
        for shift in (SHIFTS if "shift" in cols else ["AM"]):
            payload = {
                "tenant_id": TENANT,
                "outlet": rnd.choice(OUTLETS),
                "date": today(d),
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
        "POS terminal froze",
        "Short on glassware",
        "Oven preheat slow",
        "Spill at entrance",
        "Supplier late delivery",
        "Card reader intermittent",
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
    for name, category in base:
        qty_val = rnd.randint(20, 120)
        sold_on_val = today(-rnd.randint(0, 6))
        payload = {
            "tenant_id": TENANT,
            "name": name,
            "qty": qty_val,
            "sold_on": sold_on_val,
            "category": category,
            "units_sold": qty_val,
            "revenue_cents": cents(300, 2200),
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

        # Steward 2.0 demo data
        tmpl = ChecklistTemplate(
            tenant_id=TENANT,
            name="Daily Open/Close",
            schema_json='{"fields":[{"type":"boolean","id":"lights","label":"Lights checked"},{"type":"boolean","id":"fridges","label":"Fridges within temp"},{"type":"text","id":"notes","label":"Notes"}]}'
        )
        db.add(tmpl)
        db.flush()
        db.add(
            ChecklistResponse(
                tenant_id=TENANT,
                template_id=tmpl.id,
                filled_by="System",
                location="Main",
                answers_json='{"lights":true,"fridges":true,"notes":"Auto-seeded"}',
            )
        )

        v1 = Vehicle(tenant_id=TENANT, reg="CA 123-456", make="Toyota", model="Hilux", status="AVAILABLE")
        v2 = Vehicle(tenant_id=TENANT, reg="CA 789-012", make="VW", model="Caddy", status="SERVICE")
        db.add_all([v1, v2])
        db.flush()
        db.add(
            VehicleBooking(
                tenant_id=TENANT,
                vehicle_id=v1.id,
                booked_by="Ops",
                start_at=now_minus(240),
                end_at=now_minus(120),
                purpose="Supplier pickup",
            )
        )

        db.add(
            CapaAction(
                tenant_id=TENANT,
                incident_id=1,
                title="Replace cracked glassware",
                owner="Manager",
                status="OPEN",
            )
        )

        db.commit()
        print("✓ Seeding complete for tenant:", TENANT)
    finally:
        db.close()


if __name__ == "__main__":
    ensure_seed()

