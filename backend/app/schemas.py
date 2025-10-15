from __future__ import annotations

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, field_validator
import json

class HandoverBase(BaseModel):
    outlet: str
    date: datetime
    shift: str
    period: str
    bookings: int
    walk_ins: int
    covers: int
    food_revenue: float
    beverage_revenue: float
    top_sales: List[str] = []

class HandoverCreate(HandoverBase):
    pass

class HandoverOut(HandoverBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # be tolerant of legacy JSON strings
    @field_validator("top_sales", mode="before")
    @classmethod
    def _coerce_top_sales(cls, v):
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else [str(parsed)]
            except Exception:
                return [v]
        return v

    class Config:
        from_attributes = True

# alias expected by your routes
HandoverRead = HandoverOut

class GuestNoteBase(BaseModel):
    guest_name: str
    note: str

class GuestNoteCreate(GuestNoteBase):
    pass

class GuestNoteOut(GuestNoteBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
