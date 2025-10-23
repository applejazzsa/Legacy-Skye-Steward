# app/api/handover.py
from __future__ import annotations
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import Handover
from ..tenant import get_tenant

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def cols(model) -> set[str]:
    return set(model.__table__.columns.keys())

def serialize(obj) -> Dict[str, Any]:
    data = {}
    for c in obj.__table__.columns.keys():
        val = getattr(obj, c)
        # cast decimals/bytes if any; otherwise FastAPI handles
        data[c] = val
    return data

@router.get("", response_model=list[dict])
def list_handovers(
    db: Session = Depends(get_db),
    tenant: str = Depends(get_tenant),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    q = db.query(Handover).filter(Handover.tenant_id == tenant)
    # prefer ordering by date desc then id desc if present
    model_cols = cols(Handover)
    if "date" in model_cols and "id" in model_cols:
        q = q.order_by(Handover.date.desc(), Handover.id.desc())
    elif "id" in model_cols:
        q = q.order_by(Handover.id.desc())

    items: List[Handover] = q.limit(limit).offset(offset).all()
    return [serialize(x) for x in items]
