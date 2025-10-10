from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, String
from app import models

# Helper: normalize dates
def as_date(dt: datetime | date) -> date:
    if isinstance(dt, datetime):
        return dt.date()
    return dt

def date_range(start: date, end: date) -> Tuple[datetime, datetime]:
    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(end, datetime.max.time())
    return start_dt, end_dt

# -----------------------------
# DAILY REPORT
# -----------------------------
def daily_kpis(db: Session, target: date, outlet: Optional[str] = None) -> Dict[str, Any]:
    start_dt, end_dt = date_range(target, target)

    q = db.query(
        models.Handover.outlet.label("outlet"),
        models.Handover.period.label("period"),
        func.sum(models.Handover.bookings).label("bookings"),
        func.sum(models.Handover.walk_ins).label("walk_ins"),
        func.sum(models.Handover.covers).label("covers"),
        func.sum(models.Handover.food_revenue).label("food_revenue"),
        func.sum(models.Handover.beverage_revenue).label("beverage_revenue"),
    ).filter(models.Handover.date >= start_dt, models.Handover.date <= end_dt)

    if outlet:
        q = q.filter(models.Handover.outlet.ilike(outlet))

    q = q.group_by(models.Handover.outlet, models.Handover.period).order_by(models.Handover.outlet, models.Handover.period)

    rows = q.all()
    data: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        out = r.outlet
        if out not in data:
            data[out] = {"outlet": out, "periods": []}
        data[out]["periods"].append({
            "period": r.period.value if hasattr(r.period, "value") else r.period,
            "bookings": int(r.bookings or 0),
            "walk_ins": int(r.walk_ins or 0),
            "covers": int(r.covers or 0),
            "food_revenue": float(r.food_revenue or 0.0),
            "beverage_revenue": float(r.beverage_revenue or 0.0),
            "total_revenue": float((r.food_revenue or 0.0) + (r.beverage_revenue or 0.0)),
        })

    # incident summary
    qi = db.query(
        models.Incident.outlet,
        models.Incident.severity,
        func.count(models.Incident.id)
    ).filter(models.Incident.date >= start_dt, models.Incident.date <= end_dt)

    if outlet:
        qi = qi.filter(models.Incident.outlet.ilike(outlet))

    qi = qi.group_by(models.Incident.outlet, models.Incident.severity)
    inc_raw = qi.all()

    incidents: Dict[str, Dict[str, int]] = {}
    for out, sev, count in inc_raw:
        out_key = out
        if out_key not in incidents:
            incidents[out_key] = {}
        sev_val = sev.value if hasattr(sev, "value") else sev
        incidents[out_key][sev_val] = int(count)

    return {
        "date": target.isoformat(),
        "outlets": list(data.values()),
        "incidents": incidents
    }

# -----------------------------
# WEEKLY REPORT (Mon–Sun)
# -----------------------------
def week_bounds(any_day: date) -> Tuple[date, date]:
    # Monday as start of week
    start = any_day - timedelta(days=any_day.weekday())
    end = start + timedelta(days=6)
    return start, end

def weekly_rollup(db: Session, for_day: date, outlet: Optional[str] = None) -> Dict[str, Any]:
    start, end = week_bounds(for_day)
    start_dt, end_dt = date_range(start, end)

    q = db.query(
        models.Handover.outlet.label("outlet"),
        func.date(cast(models.Handover.date, String)).label("day"),
        func.sum(models.Handover.covers).label("covers"),
        func.sum(models.Handover.food_revenue).label("food_revenue"),
        func.sum(models.Handover.beverage_revenue).label("beverage_revenue"),
    ).filter(models.Handover.date >= start_dt, models.Handover.date <= end_dt)

    if outlet:
        q = q.filter(models.Handover.outlet.ilike(outlet))

    q = q.group_by(models.Handover.outlet, func.date(cast(models.Handover.date, String))) \
         .order_by(models.Handover.outlet, func.date(cast(models.Handover.date, String)))

    rows = q.all()
    by_outlet: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        out = r.outlet
        if out not in by_outlet:
            by_outlet[out] = []
        by_outlet[out].append({
            "date": str(r.day),
            "covers": int(r.covers or 0),
            "food_revenue": float(r.food_revenue or 0.0),
            "beverage_revenue": float(r.beverage_revenue or 0.0),
            "total_revenue": float((r.food_revenue or 0.0) + (r.beverage_revenue or 0.0)),
        })

    # incident open vs resolved in the week
    qi = db.query(
        models.Incident.outlet,
        models.Incident.status,
        func.count(models.Incident.id)
    ).filter(models.Incident.date >= start_dt, models.Incident.date <= end_dt)

    if outlet:
        qi = qi.filter(models.Incident.outlet.ilike(outlet))

    qi = qi.group_by(models.Incident.outlet, models.Incident.status)
    inc = qi.all()

    inc_summary: Dict[str, Dict[str, int]] = {}
    for out, status, count in inc:
        out_key = out
        if out_key not in inc_summary:
            inc_summary[out_key] = {}
        st = status.value if hasattr(status, "value") else status
        inc_summary[out_key][st] = int(count)

    # totals per outlet
    totals: Dict[str, Dict[str, float]] = {}
    for out, daily in by_outlet.items():
        t_cov = sum(d["covers"] for d in daily)
        t_food = sum(d["food_revenue"] for d in daily)
        t_bev = sum(d["beverage_revenue"] for d in daily)
        totals[out] = {
            "covers": t_cov,
            "food_revenue": round(t_food, 2),
            "beverage_revenue": round(t_bev, 2),
            "total_revenue": round(t_food + t_bev, 2),
            "days_counted": len(daily)
        }

    return {
        "week_start": start.isoformat(),
        "week_end": end.isoformat(),
        "daily": by_outlet,
        "totals": totals,
        "incidents": inc_summary
    }
