from __future__ import annotations

from datetime import datetime, date
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..db import get_db, engine
from ..tenant import get_tenant

router = APIRouter(prefix="/api/guest-notes", tags=["guest-notes"])


def _ensure_table():
    sql = """
    CREATE TABLE IF NOT EXISTS guest_notes (
        id INTEGER PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        when_ts TEXT NOT NULL,
        author TEXT NOT NULL,
        text TEXT NOT NULL,
        room TEXT,
        status TEXT DEFAULT 'OPEN'
    );
    CREATE INDEX IF NOT EXISTS ix_guest_notes_tenant_when ON guest_notes(tenant_id, when_ts);
    """
    with engine.begin() as conn:
        for stmt in sql.split(";"):
            s = stmt.strip()
            if s:
                conn.execute(text(s))


def _row_to_dict(row: Any) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "tenant": row["tenant_id"],
        "when": row["when_ts"],
        "author": row["author"],
        "text": row["text"],
        "room": row["room"],
        "status": row["status"],
    }


@router.get("", response_model=list[dict])
def list_guest_notes(
    tenant: str = Depends(get_tenant),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
):
    _ensure_table()
    clauses = ["tenant_id = :tenant"]
    params: Dict[str, Any] = {"tenant": tenant}
    if date_from:
        clauses.append("date(when_ts) >= :df")
        params["df"] = str(date_from)
    if date_to:
        clauses.append("date(when_ts) <= :dt")
        params["dt"] = str(date_to)
    sql = f"SELECT * FROM guest_notes WHERE {' AND '.join(clauses)} ORDER BY when_ts DESC LIMIT 100"
    with engine.begin() as conn:
        rows = conn.execute(text(sql), params).mappings().all()
    return [_row_to_dict(r) for r in rows]


@router.post("", response_model=dict)
def create_guest_note(payload: Dict[str, Any], tenant: str = Depends(get_tenant)):
    _ensure_table()
    when_ts = payload.get("when") or datetime.utcnow().isoformat()
    author = (payload.get("author") or "").strip() or "Anonymous"
    textv = (payload.get("text") or "").strip()
    if not textv:
        raise HTTPException(status_code=400, detail="text required")
    room = payload.get("room")
    status = (payload.get("status") or "OPEN").upper()
    with engine.begin() as conn:
        res = conn.execute(
            text(
                "INSERT INTO guest_notes (tenant_id, when_ts, author, text, room, status) "
                "VALUES (:t, :w, :a, :x, :r, :s)"
            ),
            {"t": tenant, "w": when_ts, "a": author, "x": textv, "r": room, "s": status},
        )
        new_id = res.lastrowid
        row = conn.execute(text("SELECT * FROM guest_notes WHERE id = :id"), {"id": new_id}).mappings().first()
    return _row_to_dict(row)
