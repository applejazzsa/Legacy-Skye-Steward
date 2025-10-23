from pydantic import BaseModel, Field
from typing import Optional, List

class IncidentCreate(BaseModel):
    outlet: str = Field(..., min_length=1, max_length=120)
    severity: str = Field(..., min_length=1, max_length=20)
    title: str = Field(..., min_length=1, max_length=200)

class IncidentUpdate(BaseModel):
    status: Optional[str] = Field(None, min_length=1, max_length=20)

class IncidentOut(BaseModel):
    id: int
    tenant_id: str
    outlet: str
    severity: str
    title: str
    status: str
    created_at: str

    class Config:
        orm_mode = True

class IncidentList(BaseModel):
    total: int
    items: List[IncidentOut]
