from datetime import datetime, timedelta
from typing import List

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Handover, GuestNote, Incident
from .schemas import IncidentCreate

# ---- Handovers ----
def list_handovers(db: Session) -> List[Handover]:
    return db.execute(select(Handover).order_by(Handover.date.desc())).scalars().all()

# ---- Guest Notes ----
def list_guest_notes(db: Session) -> List[GuestNote]:
    return db.execute(select(GuestNote).order_by(GuestNote.created_at.desc())).scalars().all()

# ---- Incidents (NEW) ----
def list_incidents(db: Session) -> List[Incident]:
    return db.execute(select(Incident).order_by(Incident.created_at.desc())).scalars().all()

def create_incident(db: Session, payload: IncidentCreate) -> Incident:
    obj = Incident(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

# ---- Analytics helpers ----
def kpi_summary(db: Session, target: float):
    # simple 7-day window
    end = datetime.utcnow()
    start = end - timedelta(days=7)

    rows = db.execute(
        select(
            func.count().label("covers"), 
            func.coalesce(func.sum(Handover.food_revenue + Handover.beverage_revenue), 0.0)
        ).where(Handover.date >= start, Handover.date <= end)
    ).one()

    covers = rows[0] or 0
    revenue = float(rows[1] or 0.0)
    avg_check = (revenue / covers) if covers else 0.0

    prev_start = start - timedelta(days=7)
    prev_end = start
    prev_rev = float(
        db.execute(
            select(func.coalesce(func.sum(Handover.food_revenue + Handover.beverage_revenue), 0.0))
            .where(Handover.date >= prev_start, Handover.date <= prev_end)
        ).scalar() or 0.0
    )
    delta = revenue - prev_rev

    return {
        "window": f"{start.date()} \u2192 {end.date()}",
        "covers": covers,
        "revenue": revenue,
        "avg_check": avg_check,
        "revenue_vs_prev": delta,
        "target": target,
        "target_gap": target - revenue,
    }

def top_items(db: Session, limit: int):
    # flatten top_sales arrays
    from collections import Counter
    items: Counter[str] = Counter()
    for h in db.execute(select(Handover.top_sales)).all():
        for name in (h[0] or []):
            items[name] += 1
    return [{"item": k, "count": v} for k, v in items.most_common(limit)]

def weekly_revenue(db: Session, weeks: int):
    from collections import defaultdict
    buckets = defaultdict(float)
    for h in db.execute(select(Handover.date, Handover.food_revenue, Handover.beverage_revenue)).all():
        iso_year, iso_week, _ = h[0].isocalendar()
        key = f"{iso_year}-W{iso_week:02d}"
        buckets[key] += float((h[1] or 0) + (h[2] or 0))
    keys = sorted(buckets.keys())[-weeks:]
    return [{"week": k, "revenue": buckets[k], "covers": 0} for k in keys]
