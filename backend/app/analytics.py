"""Analytics utilities for the hospitality handover system."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, time, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import GuestNote, Handover

def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_iso_datetime(value: str | None) -> datetime | None:
    """Parse ISO8601 datetimes without relying on external libraries."""

    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return _to_utc(datetime.fromisoformat(value))


def default_window(days: int = 7) -> tuple[datetime, datetime]:
    """Return the default analytics window covering the last *days* calendar days."""

    now = datetime.now(timezone.utc)
    end_date = datetime.combine(now.date(), time.max, tzinfo=timezone.utc)
    start_date = datetime.combine(
        (end_date - timedelta(days=days - 1)).date(),
        time.min,
        tzinfo=timezone.utc,
    )
    return start_date, end_date


def normalize_window(
    start: datetime | None,
    end: datetime | None,
    *,
    default_days: int = 7,
) -> tuple[datetime, datetime]:
    """Ensure a valid date window is produced, falling back to defaults."""

    if start and end:
        if start > end:
            start, end = end, start
        return _to_utc(start), _to_utc(end)

    if start and not end:
        start = _to_utc(start)
        end = datetime.combine(start.date(), time.max, tzinfo=timezone.utc)
        return start, end

    if end and not start:
        end = _to_utc(end)
        start = datetime.combine(end.date() - timedelta(days=default_days - 1), time.min, tzinfo=timezone.utc)
        return start, end

    return default_window(default_days)


def _handover_range_query(
    db: Session,
    start: datetime,
    end: datetime,
    outlet: str | None,
):
    stmt = select(Handover).where(Handover.date >= start, Handover.date <= end)
    if outlet:
        stmt = stmt.where(Handover.outlet == outlet)
    return db.scalars(stmt)


def _guest_note_range_query(
    db: Session,
    start: datetime,
    end: datetime,
    outlet: str | None,
):
    stmt = select(GuestNote).where(GuestNote.date >= start, GuestNote.date <= end)
    if outlet:
        stmt = stmt.where(GuestNote.outlet == outlet)
    return db.scalars(stmt)


def top_items(
    db: Session,
    *,
    start: datetime,
    end: datetime,
    outlet: str | None,
    limit: int,
) -> list[dict[str, str | int]]:
    """Return the most frequently appearing top sales items."""

    counter: Counter[str] = Counter()
    for handover in _handover_range_query(db, start, end, outlet):
        counter.update(handover.top_sales or [])
    items = [
        {"item": item, "count": count}
        for item, count in counter.most_common(limit)
    ]
    return items


def staff_praise(
    db: Session,
    *,
    start: datetime,
    end: datetime,
    outlet: str | None,
    limit: int,
) -> list[dict[str, str | int]]:
    """Return praise counts per staff member based on guest notes."""

    stmt = (
        select(GuestNote.staff, func.count(GuestNote.id))
        .where(GuestNote.date >= start, GuestNote.date <= end)
    )
    if outlet:
        stmt = stmt.where(GuestNote.outlet == outlet)
    stmt = stmt.group_by(GuestNote.staff).order_by(func.count(GuestNote.id).desc())
    results = db.execute(stmt).all()
    return [{"staff": staff, "count": count} for staff, count in results[:limit]]


def _aggregate_kpis(db: Session, start: datetime, end: datetime, outlet: str | None) -> dict[str, float | int]:
    stmt = select(
        func.coalesce(func.sum(Handover.covers), 0),
        func.coalesce(func.sum(Handover.food_revenue), 0.0),
        func.coalesce(func.sum(Handover.beverage_revenue), 0.0),
    ).where(Handover.date >= start, Handover.date <= end)
    if outlet:
        stmt = stmt.where(Handover.outlet == outlet)
    covers, food_revenue, beverage_revenue = db.execute(stmt).one()
    covers = int(covers or 0)
    food_revenue = float(food_revenue or 0.0)
    beverage_revenue = float(beverage_revenue or 0.0)
    total_revenue = food_revenue + beverage_revenue
    avg_check = total_revenue / covers if covers else 0.0
    return {
        "covers": covers,
        "food_revenue": food_revenue,
        "beverage_revenue": beverage_revenue,
        "total_revenue": total_revenue,
        "avg_check": avg_check,
    }


def _pct_change(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100.0


def kpi_summary(
    db: Session,
    *,
    start: datetime,
    end: datetime,
    outlet: str | None,
    target: float,
) -> dict[str, object]:
    """Return KPI summary for the specified window and comparison."""

    current = _aggregate_kpis(db, start, end, outlet)
    window_delta = end - start
    previous_end = start - timedelta(seconds=1)
    previous_start = previous_end - window_delta
    previous = _aggregate_kpis(db, previous_start, previous_end, outlet)

    change_pct = {
        "covers": _pct_change(current["covers"], previous["covers"]),
        "total_revenue": _pct_change(current["total_revenue"], previous["total_revenue"]),
        "avg_check": _pct_change(current["avg_check"], previous["avg_check"]),
    }

    achievement_pct = (current["total_revenue"] / target * 100.0) if target else 0.0

    return {
        "window": {
            "start": _to_utc(start),
            "end": _to_utc(end),
        },
        "current": current,
        "previous": previous,
        "change_pct": change_pct,
        "target": {
            "total_revenue_target": float(target),
            "achievement_pct": achievement_pct,
        },
    }


__all__ = [
    "parse_iso_datetime",
    "default_window",
    "normalize_window",
    "top_items",
    "staff_praise",
    "kpi_summary",
]
