from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import CapaAction
from ..tenant import get_tenant

router = APIRouter(prefix="/api/capa", tags=["capa"])


def serialize(obj) -> Dict[str, Any]:
    return {c: getattr(obj, c) for c in obj.__table__.columns.keys()}


@router.get("/actions", response_model=list[dict])
def list_actions(db: Session = Depends(get_db), tenant: str = Depends(get_tenant)):
    rows = (
        db.query(CapaAction)
        .filter(CapaAction.tenant_id == tenant)
        .order_by(CapaAction.created_at.desc())
        .limit(100)
        .all()
    )
    return [serialize(x) for x in rows]


@router.post("/actions", response_model=dict)
def create_action(payload: Dict[str, Any], db: Session = Depends(get_db), tenant: str = Depends(get_tenant)):
    incident_id = int(payload.get("incident_id") or 0)
    title = (payload.get("title") or "").strip()
    if not incident_id or not title:
        raise HTTPException(status_code=400, detail="incident_id and title required")
    row = CapaAction(
        tenant_id=tenant,
        incident_id=incident_id,
        title=title,
        owner=payload.get("owner"),
        status=payload.get("status") or "OPEN",
        due_date=payload.get("due_date"),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize(row)


@router.post("/actions/{action_id}/close", response_model=dict)
def close_action(action_id: int, db: Session = Depends(get_db), tenant: str = Depends(get_tenant)):
    row = db.query(CapaAction).filter(CapaAction.id == action_id, CapaAction.tenant_id == tenant).first()
    if not row:
        raise HTTPException(status_code=404, detail="action not found")
    row.status = "DONE"
    db.commit()
    db.refresh(row)
    return serialize(row)

