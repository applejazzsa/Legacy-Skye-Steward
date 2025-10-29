from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import text

from ..db import engine
from ..tenant import get_tenant

router = APIRouter(prefix="/api/concierge", tags=["concierge"])


def _ensure():
    with engine.begin() as conn:
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS concierge_logs (
                id INTEGER PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                when_ts TEXT NOT NULL,
                author TEXT,
                text TEXT NOT NULL,
                tags TEXT
            );
            """
        ))


@router.get("", response_model=list[dict])
def list_logs(
    tenant: str = Depends(get_tenant),
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
    limit: int = Query(100, ge=1, le=500),
):
    _ensure()
    where = ["tenant_id = :t"]; p: Dict[str, Any] = {"t": tenant}
    if date_from: where.append("date(when_ts) >= :df"); p["df"] = date_from
    if date_to: where.append("date(when_ts) <= :dt"); p["dt"] = date_to
    sql = f"SELECT * FROM concierge_logs WHERE {' AND '.join(where)} ORDER BY when_ts DESC LIMIT :lim"; p["lim"] = int(limit)
    with engine.begin() as conn:
        rows = conn.execute(text(sql), p).mappings().all()
    return [dict(r) for r in rows]


@router.post("", response_model=dict)
def create_log(payload: Dict[str, Any], tenant: str = Depends(get_tenant)):
    _ensure()
    txt = (payload.get("text") or "").strip()
    if not txt:
        raise HTTPException(status_code=400, detail="text required")
    when = payload.get("when_ts") or datetime.utcnow().isoformat()
    with engine.begin() as conn:
        res = conn.execute(text("INSERT INTO concierge_logs (tenant_id, when_ts, author, text, tags) VALUES (:t,:w,:a,:x,:g)"),
                           {"t": tenant, "w": when, "a": payload.get("author"), "x": txt, "g": payload.get("tags")})
        new_id = res.lastrowid
        row = conn.execute(text("SELECT * FROM concierge_logs WHERE id=:id"), {"id": new_id}).mappings().first()
    return dict(row)

