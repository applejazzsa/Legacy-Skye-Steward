from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from ..db import engine
from ..tenant import get_tenant

router = APIRouter(prefix="/api/spa", tags=["spa"])


def _ensure_tables():
    sql = """
    CREATE TABLE IF NOT EXISTS spa_therapists (
        id INTEGER PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        name TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS spa_treatments (
        id INTEGER PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        name TEXT NOT NULL,
        duration_min INTEGER NOT NULL DEFAULT 60
    );
    CREATE TABLE IF NOT EXISTS spa_visits (
        id INTEGER PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        when_ts TEXT NOT NULL,
        guest_name TEXT,
        therapist_id INTEGER,
        treatment_id INTEGER,
        upgrade TEXT,
        occasion TEXT,
        feedback TEXT,
        amount REAL
    );
    """
    with engine.begin() as conn:
        for stmt in sql.split(";"):
            s = stmt.strip()
            if s:
                conn.execute(text(s))
        # add amount column if missing (SQLite pragma)
        cols = {r[1] for r in conn.execute(text("PRAGMA table_info(spa_visits)"))}
        if "amount" not in cols:
            conn.execute(text("ALTER TABLE spa_visits ADD COLUMN amount REAL"))


@router.get("/therapists", response_model=list[dict])
def list_therapists(tenant: str = Depends(get_tenant)):
    _ensure_tables()
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT * FROM spa_therapists WHERE tenant_id=:t ORDER BY name"), {"t": tenant}).mappings().all()
    return [dict(r) for r in rows]


@router.get("/treatments", response_model=list[dict])
def list_treatments(tenant: str = Depends(get_tenant)):
    _ensure_tables()
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT * FROM spa_treatments WHERE tenant_id=:t ORDER BY name"), {"t": tenant}).mappings().all()
    return [dict(r) for r in rows]


@router.post("/therapists", response_model=dict)
def create_therapist(payload: Dict[str, Any], tenant: str = Depends(get_tenant)):
    _ensure_tables()
    name = (payload.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name required")
    with engine.begin() as conn:
        res = conn.execute(text("INSERT INTO spa_therapists (tenant_id, name) VALUES (:t, :n)"), {"t": tenant, "n": name})
        new_id = res.lastrowid
        row = conn.execute(text("SELECT * FROM spa_therapists WHERE id=:id"), {"id": new_id}).mappings().first()
    return dict(row)


@router.post("/treatments", response_model=dict)
def create_treatment(payload: Dict[str, Any], tenant: str = Depends(get_tenant)):
    _ensure_tables()
    name = (payload.get("name") or "").strip()
    duration = int(payload.get("duration_min") or 60)
    if not name:
        raise HTTPException(status_code=400, detail="name required")
    with engine.begin() as conn:
        res = conn.execute(text("INSERT INTO spa_treatments (tenant_id, name, duration_min) VALUES (:t, :n, :d)"), {"t": tenant, "n": name, "d": duration})
        new_id = res.lastrowid
        row = conn.execute(text("SELECT * FROM spa_treatments WHERE id=:id"), {"id": new_id}).mappings().first()
    return dict(row)


@router.post("/visits", response_model=dict)
def create_visit(payload: Dict[str, Any], tenant: str = Depends(get_tenant)):
    _ensure_tables()
    when_ts = payload.get("when") or datetime.utcnow().isoformat()
    with engine.begin() as conn:
        res = conn.execute(
            text(
                "INSERT INTO spa_visits (tenant_id, when_ts, guest_name, therapist_id, treatment_id, upgrade, occasion, feedback, amount) "
                "VALUES (:t, :w, :g, :th, :tr, :u, :o, :f, :amt)"
            ),
            {
                "t": tenant,
                "w": when_ts,
                "g": payload.get("guest_name"),
                "th": payload.get("therapist_id"),
                "tr": payload.get("treatment_id"),
                "u": payload.get("upgrade"),
                "o": payload.get("occasion"),
                "f": payload.get("feedback"),
                "amt": float(payload.get("amount") or 0.0),
            },
        )
        new_id = res.lastrowid
        row = conn.execute(text("SELECT * FROM spa_visits WHERE id=:id"), {"id": new_id}).mappings().first()
    return dict(row)


@router.get("/visits", response_model=list[dict])
def list_visits(tenant: str = Depends(get_tenant)):
    _ensure_tables()
    with engine.begin() as conn:
        rows = conn.execute(text("SELECT * FROM spa_visits WHERE tenant_id=:t ORDER BY when_ts DESC LIMIT 100"), {"t": tenant}).mappings().all()
    return [dict(r) for r in rows]
