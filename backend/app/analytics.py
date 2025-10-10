# app/analytics.py
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app import models

def _normalize_dates(
    start_date: Optional[datetime | str],
    end_date: Optional[datetime | str],
) -> Tuple[datetime, datetime]:
    if isinstance(start_date, str) and start_date:
        start_date = datetime.fromisoformat(start_date)
    if isinstance(end_date, str) and end_date:
        end_date = datetime.fromisoformat(end_date)

    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=6)

    sdt = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    edt = end_date.replace(hour=23, minute=59, second=59, microsecond=0)
    return sdt, edt

def top_items(
    db: Session,
    start_date: Optional[datetime | str],
    end_date: Optional[datetime | str],
    limit: int = 5,
    outlet: Optional[str] = None,
) -> List[Dict[str, Any]]:
    sdt, edt = _normalize_dates(start_date, end_date)

    if hasattr(models, "TopSale"):
        q = (
            db.query(
                models.TopSale.item_name.label("item"),
                func.sum(models.TopSale.quantity).label("qty"),
            )
            .filter(models.TopSale.date >= sdt, models.TopSale.date <= edt)
        )
        if outlet:
            q = q.filter(models.TopSale.outlet == outlet)
        rows = q.group_by(models.TopSale.item_name).order_by(desc("qty")).limit(limit).all()
        return [{"item": r.item, "quantity": int(r.qty)} for r in rows]

    counts: Dict[str, int] = {}
    q = db.query(models.Handover).filter(models.Handover.date >= sdt, models.Handover.date <= edt)
    if outlet:
        q = q.filter(models.Handover.outlet == outlet)

    for h in q.all():
        if not getattr(h, "top_sales", None):
            continue
        items = h.top_sales
        if isinstance(items, str):
            items = [x.strip() for x in items.split(",") if x.strip()]
        for it in items:
            counts[it] = counts.get(it, 0) + 1

    return [
        {"item": k, "quantity": v}
        for k, v in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    ]

def staff_praise(
    db: Session,
    start_date: Optional[datetime | str],
    end_date: Optional[datetime | str],
    limit: int = 5,
    outlet: Optional[str] = None,
) -> List[Dict[str, Any]]:
    if not hasattr(models, "GuestNote"):
        return []

    sdt, edt = _normalize_dates(start_date, end_date)
    q = (
        db.query(
            models.GuestNote.staff.label("staff"),
            func.count(models.GuestNote.id).label("praise_count"),
        )
        .filter(models.GuestNote.date >= sdt, models.GuestNote.date <= edt)
        .filter(models.GuestNote.sentiment == "positive")
    )
    if outlet:
        q = q.filter(models.GuestNote.outlet == outlet)

    rows = q.group_by(models.GuestNote.staff).order_by(desc("praise_count")).limit(limit).all()
    return [{"staff": r.staff or "Unspecified", "praise_count": int(r.praise_count)} for r in rows]

def kpi_summary(
    db: Session,
    target: Optional[str] = None,
    outlet: Optional[str] = None,
) -> Dict[str, Any]:
    end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)
    start = (end - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
    p_end = (start - timedelta(seconds=1)).replace(microsecond=0)
    p_start = (p_end - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)

    def rollup(sdt: datetime, edt: datetime) -> Dict[str, float]:
        q = db.query(
            func.coalesce(func.sum(models.Handover.covers), 0),
            func.coalesce(func.sum(models.Handover.food_revenue), 0.0),
            func.coalesce(func.sum(models.Handover.beverage_revenue), 0.0),
        ).filter(models.Handover.date >= sdt, models.Handover.date <= edt)
        if outlet:
            q = q.filter(models.Handover.outlet == outlet)

        covers, food_rev, bev_rev = q.one()
        covers = int(covers)
        food_rev = float(food_rev)
        bev_rev = float(bev_rev)
        total_rev = food_rev + bev_rev
        avg_check = (total_rev / covers) if covers else 0.0
        return {
            "covers": covers,
            "food_revenue": food_rev,
            "beverage_revenue": bev_rev,
            "total_revenue": total_rev,
            "avg_check": avg_check,
        }

    cur = rollup(start, end)
    prev = rollup(p_start, p_end)

    def pct(cur_v: float, prev_v: float) -> float:
        if prev_v == 0:
            return 0.0 if cur_v == 0 else 100.0
        return ((cur_v - prev_v) / prev_v) * 100.0

    summary: Dict[str, Any] = {
        "window": {"start": start.isoformat(), "end": end.isoformat()},
        "current": cur,
        "previous": prev,
        "change_pct": {
            "covers": pct(cur["covers"], prev["covers"]),
            "total_revenue": pct(cur["total_revenue"], prev["total_revenue"]),
            "avg_check": pct(cur["avg_check"], prev["avg_check"]),
        },
    }

    if target:
        try:
            t = float(target)
            summary["target"] = {
                "total_revenue_target": t,
                "achievement_pct": (cur["total_revenue"] / t * 100.0) if t > 0 else 0.0,
            }
        except Exception:
            pass

    return summary
