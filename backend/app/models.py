"""SQLAlchemy models for the hospitality domain."""
from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import DateTime, Float, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Handover(Base):
    """Operational handover information for a hospitality outlet."""

    __tablename__ = "handover"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    outlet: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    shift: Mapped[str] = mapped_column(String(50), nullable=False)
    period: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bookings: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    walk_ins: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    covers: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    food_revenue: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    beverage_revenue: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    top_sales: Mapped[List[str]] = mapped_column(JSON, nullable=False, default_factory=list)


class GuestNote(Base):
    """Compliments and notable guest feedback for staff."""

    __tablename__ = "guest_note"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    staff: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    note: Mapped[str] = mapped_column(String(500), nullable=False)
    outlet: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)


__all__ = ["Handover", "GuestNote"]
