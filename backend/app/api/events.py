from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text

from ..db import engine
from ..tenant import get_tenant
from ..deps import require_role

router = APIRouter(prefix="/api/events", tags=["events"])


def _ensure():
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, tenant_id TEXT NOT NULL, at TEXT NOT NULL, label TEXT NOT NULL)"
        ))


@router.get("", response_model=list[dict])
def list_events(tenant: str = Depends(get_tenant), date_from: Optional[str] = Query(default=None), date_to: Optional[str] = Query(default=None)):
    _ensure()
    where = ["tenant_id=:t"]; params: Dict[str, Any] = {"t": tenant}
    if date_from: where.append("date(at) >= :df"); params["df"] = date_from
    if date_to: where.append("date(at) <= :dt"); params["dt"] = date_to
    sql = f"SELECT * FROM events WHERE {' AND '.join(where)} ORDER BY at DESC"
    with engine.begin() as conn:
        rows = conn.execute(text(sql), params).mappings().all()
    return [dict(r) for r in rows]


@router.post("", response_model=dict, dependencies=[Depends(require_role("manager"))])
def create_event(payload: Dict[str, Any], tenant: str = Depends(get_tenant)):
    _ensure()
    at = (payload.get("at") or "").strip()
    label = (payload.get("label") or "").strip()
    if not at or not label:
        raise HTTPException(status_code=400, detail="at and label required")
    with engine.begin() as conn:
        res = conn.execute(text("INSERT INTO events (tenant_id, at, label) VALUES (:t,:a,:l)"), {"t": tenant, "a": at, "l": label})
        new_id = res.lastrowid
        row = conn.execute(text("SELECT * FROM events WHERE id=:id"), {"id": new_id}).mappings().first()
    return dict(row)

