from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

# -------- Handover --------
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
    top_sales: List[str] = Field(default_factory=list)

class HandoverRead(HandoverBase):
    id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

# -------- Guest Notes --------
class GuestNoteRead(BaseModel):
    id: int
    guest_name: str
    note: str
    created_at: datetime
    class Config:
        from_attributes = True

# -------- Incidents (NEW) --------
class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"

class IncidentSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class IncidentBase(BaseModel):
    title: str
    description: Optional[str] = None
    area: Optional[str] = None
    owner: Optional[str] = None
    status: IncidentStatus = IncidentStatus.OPEN
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    due_date: Optional[datetime] = None

class IncidentCreate(IncidentBase):
    pass

class IncidentRead(IncidentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    class Config:
        from_attributes = True

# -------- Analytics DTOs --------
class KpiSummary(BaseModel):
    window: str
    covers: int
    revenue: float
    avg_check: float
    revenue_vs_prev: float
    target: float
    target_gap: float

class TopItem(BaseModel):
    item: str
    count: int
