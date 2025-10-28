# app/api/incidents.py
from __future__ import annotations
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import Incident
from ..tenant import get_tenant
from ..deps import require_role

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
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
):
    q = db.query(Incident).filter(Incident.tenant_id == tenant)
    if status:
        q = q.filter(Incident.status.in_(status))
    if date_from:
        q = q.filter(Incident.created_at >= date_from)
    if date_to:
        q = q.filter(Incident.created_at <= date_to)
    # order newest first if id exists
    if "id" in Incident.__table__.columns:
        q = q.order_by(Incident.id.desc())
    items: List[Incident] = q.limit(limit).offset(offset).all()
    return [serialize(x) for x in items]

@router.post("", response_model=dict)
def create_incident(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    tenant: str = Depends(get_tenant),
    _role_ok: bool = Depends(require_role("staff")),
):
    outlet = (payload.get("outlet") or "").strip()
    severity = (payload.get("severity") or "").strip().upper() or "LOW"
    title = (payload.get("title") or "").strip()
    status = (payload.get("status") or "OPEN").strip().upper()
    if not outlet or not title:
        raise HTTPException(status_code=400, detail="outlet and title required")
    row = Incident(tenant_id=tenant, outlet=outlet, severity=severity, title=title, status=status)
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize(row)


@router.patch("/{incident_id}", response_model=dict)
def update_incident(
    incident_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    tenant: str = Depends(get_tenant),
    _role_ok: bool = Depends(require_role("manager")),
):
    row: Optional[Incident] = (
        db.query(Incident).filter(Incident.id == incident_id, Incident.tenant_id == tenant).first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="incident not found")
    # Allowed updates: outlet, title, severity, status
    outlet = (payload.get("outlet") or None)
    title = (payload.get("title") or None)
    severity = (payload.get("severity") or None)
    status = (payload.get("status") or None)
    if outlet is not None:
        row.outlet = str(outlet)
    if title is not None:
        row.title = str(title)
    if severity is not None:
        row.severity = str(severity).upper()
    if status is not None:
        row.status = str(status).upper()
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize(row)
