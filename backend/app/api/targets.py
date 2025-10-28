from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from ..db import engine
from ..tenant import get_tenant
from ..deps import require_role

router = APIRouter(prefix="/api/analytics/targets", tags=["targets"])


def _ensure():
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS dept_targets (tenant_id TEXT NOT NULL, dept TEXT NOT NULL, target REAL NOT NULL, PRIMARY KEY(tenant_id, dept))"
        ))


@router.get("", response_model=List[Dict[str, Any]])
def list_targets(tenant: str = Depends(get_tenant)):
    _ensure()
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT dept, target FROM dept_targets WHERE tenant_id=:t"), {"t": tenant}).mappings().all()
    return [dict(r) for r in rows]


@router.post("", response_model=dict, dependencies=[Depends(require_role("manager"))])
def upsert_target(payload: Dict[str, Any], tenant: str = Depends(get_tenant)):
    _ensure()
    dept = (payload.get("dept") or "").strip()
    target = float(payload.get("target") or 0)
    if not dept:
        raise HTTPException(status_code=400, detail="dept required")
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO dept_targets (tenant_id, dept, target) VALUES (:t,:d,:v) ON CONFLICT(tenant_id,dept) DO UPDATE SET target=:v"), {"t": tenant, "d": dept, "v": target})
        row = conn.execute(text("SELECT dept, target FROM dept_targets WHERE tenant_id=:t AND dept=:d"), {"t": tenant, "d": dept}).mappings().first()
    return dict(row)

