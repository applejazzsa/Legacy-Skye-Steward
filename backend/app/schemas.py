"""Pydantic models for request and response payloads."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class GuestNoteBase(BaseModel):
    date: datetime
    staff: str
    note: str
    outlet: Optional[str] = None


class GuestNoteRead(GuestNoteBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class HandoverBase(BaseModel):
    outlet: str
    date: datetime
    shift: str
    period: Optional[str] = None
    bookings: int = 0
    walk_ins: int = 0
    covers: int = 0
    food_revenue: float = 0.0
    beverage_revenue: float = 0.0
    top_sales: List[str] = Field(default_factory=list)


class HandoverCreate(HandoverBase):
    """Schema for creating a new handover."""


class HandoverRead(HandoverBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class KPIChange(BaseModel):
    covers: float
    total_revenue: float
    avg_check: float


class KPIValues(BaseModel):
    covers: int
    food_revenue: float
    beverage_revenue: float
    total_revenue: float
    avg_check: float


class KPIWindow(BaseModel):
    start: datetime
    end: datetime


class KPITarget(BaseModel):
    total_revenue_target: float
    achievement_pct: float


class KPISummary(BaseModel):
    window: KPIWindow
    current: KPIValues
    previous: KPIValues
    change_pct: KPIChange
    target: KPITarget


__all__ = [
    "GuestNoteRead",
    "HandoverCreate",
    "HandoverRead",
    "KPISummary",
]
