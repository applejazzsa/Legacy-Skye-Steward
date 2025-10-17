# backend/app/schemas/incidents.py
from __future__ import annotations
from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

# ----- Input payloads -----

class IncidentCreate(BaseModel):
    tenant_id: str = Field(..., min_length=1)
    outlet: str = Field(..., min_length=1, max_length=120)
    severity: Literal["low", "medium", "high"] = "low"
    title: str = Field(..., min_length=1, max_length=200)

class IncidentUpdate(BaseModel):
    # Allow partial updates; API can choose which fields to honor
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    severity: Optional[Literal["low", "medium", "high"]] = None
    status: Optional[Literal["open", "closed"]] = None

# ----- Output payloads -----

class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2 replacement for orm_mode

    id: int
    tenant_id: str
    outlet: str
    severity: Literal["low", "medium", "high"]
    title: str
    status: Literal["open", "closed"]
    created_at: datetime

class IncidentList(BaseModel):
    items: List[IncidentOut]
    total: int
