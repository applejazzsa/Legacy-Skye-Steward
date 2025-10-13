"""Database access helpers for handovers."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Handover
from .schemas import HandoverCreate


def create_handover(db: Session, data: HandoverCreate) -> Handover:
    """Create and persist a new handover record."""

    handover = Handover(
        outlet=data.outlet,
        date=data.date,
        shift=data.shift,
        period=data.period,
        bookings=data.bookings,
        walk_ins=data.walk_ins,
        covers=data.covers,
        food_revenue=data.food_revenue,
        beverage_revenue=data.beverage_revenue,
        top_sales=list(data.top_sales),
    )
    db.add(handover)
    db.commit()
    db.refresh(handover)
    return handover


def list_handovers(
    db: Session,
    *,
    outlet: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> list[Handover]:
    """Return handovers filtered by outlet and date range."""

    stmt = select(Handover)
    if outlet:
        stmt = stmt.where(Handover.outlet == outlet)
    if start_date:
        stmt = stmt.where(Handover.date >= start_date)
    if end_date:
        stmt = stmt.where(Handover.date <= end_date)
    stmt = stmt.order_by(Handover.date.desc())
    return list(db.scalars(stmt))


__all__ = ["create_handover", "list_handovers"]
