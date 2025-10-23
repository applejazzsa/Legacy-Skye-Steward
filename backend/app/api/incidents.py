# app/api/incidents.py
from __future__ import annotations
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import Incident
from ..tenant import get_tenant

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def serialize(obj) -> Dict[str, Any]:
    return {c: getattr(obj, c) for c in obj.__table__.columns.keys()}

@router.get("", response_model=list[dict])
def list_incidents(
    db: Session = Depends(get_db),
    tenant: str = Depends(get_tenant),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: List[str] = Query(default=["OPEN", "IN_PROGRESS"]),
):
    q = db.query(Incident).filter(Incident.tenant_id == tenant)
    if status:
        q = q.filter(Incident.status.in_(status))
    # order newest first if id exists
    if "id" in Incident.__table__.columns:
        q = q.order_by(Incident.id.desc())
    items: List[Incident] = q.limit(limit).offset(offset).all()
    return [serialize(x) for x in items]
