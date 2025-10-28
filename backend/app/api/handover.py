# app/api/handover.py
from __future__ import annotations
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import Handover
from ..tenant import get_tenant
from ..deps import require_role

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

@router.post("", response_model=dict)
def create_handover(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    tenant: str = Depends(get_tenant),
    _role_ok: bool = Depends(require_role("manager")),
):
    outlet = (payload.get("outlet") or "").strip()
    shift = (payload.get("shift") or "").strip().upper() or "AM"
    date = payload.get("date")
    covers = int(payload.get("covers") or 0)
    if not outlet or not date:
        raise HTTPException(status_code=400, detail="outlet and date required")
    row = Handover(tenant_id=tenant, outlet=outlet, shift=shift, date=date, covers=covers)
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize(row)


@router.patch("/{handover_id}", response_model=dict)
def update_handover(
    handover_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    tenant: str = Depends(get_tenant),
    _role_ok: bool = Depends(require_role("manager")),
):
    row = db.query(Handover).filter(Handover.id == handover_id, Handover.tenant_id == tenant).first()
    if not row:
        raise HTTPException(status_code=404, detail="handover not found")
    # Allowed updates
    if "date" in payload and payload["date"]:
        row.date = payload["date"]
    if "outlet" in payload and payload["outlet"] is not None:
        row.outlet = str(payload["outlet"]).strip()
    if "shift" in payload and payload["shift"]:
        row.shift = str(payload["shift"]).strip().upper()
    if "covers" in payload and payload["covers"] is not None:
        try:
            c = int(payload["covers"])  # type: ignore
            row.covers = max(0, c)
        except Exception:
            row.covers = 0
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize(row)
