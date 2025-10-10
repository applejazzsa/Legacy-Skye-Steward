# app/schemas.py
from __future__ import annotations
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# ---------- Handover ----------

class HandoverBase(BaseModel):
    outlet: str = Field(..., examples=["Main Restaurant"])
    date: datetime = Field(..., examples=["2025-09-29T09:26:50.982Z"])
    shift: Optional[str] = Field(None, examples=["AM", "PM"])
    period: Optional[str] = Field(None, examples=["BREAKFAST", "LUNCH", "DINNER"])
    bookings: int = 0
    walk_ins: int = 0
    covers: int = 0
    food_revenue: float = 0.0
    beverage_revenue: float = 0.0
    top_sales: Optional[List[str]] = None

class HandoverCreate(HandoverBase):
    pass

class HandoverUpdate(BaseModel):
    outlet: Optional[str] = None
    date: Optional[datetime] = None
    shift: Optional[str] = None
    period: Optional[str] = None
    bookings: Optional[int] = None
    walk_ins: Optional[int] = None
    covers: Optional[int] = None
    food_revenue: Optional[float] = None
    beverage_revenue: Optional[float] = None
    top_sales: Optional[List[str]] = None

class HandoverRead(HandoverBase):
    id: int

    class Config:
        from_attributes = True
