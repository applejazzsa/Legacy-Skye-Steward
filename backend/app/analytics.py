from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session
from app.models import Handover

def get_top_items(db: Session, limit: int = 5) -> List[str]:
    since = datetime.utcnow() - timedelta(days=30)
    rows = db.execute(select(Handover.top_sales).where(Handover.date >= since)).all()
    counts: Dict[str, int] = {}
    for (arr,) in rows:
        if not arr:
            continue
        for item in arr:
            counts[item] = counts.get(item, 0) + 1
    return [k for k, _ in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:limit]]

def get_kpi_summary(db: Session, target: float) -> Dict[str, Any]:
    now = datetime.utcnow()
    start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)

    def window(a: datetime, b: datetime) -> Dict[str, float]:
        where = and_(Handover.date >= a, Handover.date <= b)
        covers = db.execute(select(func.coalesce(func.sum(Handover.covers), 0)).where(where)).scalar_one()
        food   = db.execute(select(func.coalesce(func.sum(Handover.food_revenue), 0.0)).where(where)).scalar_one()
        bev    = db.execute(select(func.coalesce(func.sum(Handover.beverage_revenue), 0.0)).where(where)).scalar_one()
        return {"covers": float(covers), "food": float(food), "beverage": float(bev), "rev": float(food + bev)}

    curr = window(start, end)
    return {
        "week_start": start.isoformat(),
        "week_end": end.isoformat(),
        "covers": curr["covers"],
        "revenue": curr["rev"],
        "progress": (curr["rev"] / target) if target else 0.0,
    }
