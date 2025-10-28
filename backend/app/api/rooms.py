from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text

from ..db import engine
from ..tenant import get_tenant
from ..deps import require_role

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


def _ensure_tables():
    sql = """
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        name TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'AVAILABLE',
        housekeeping_status TEXT NOT NULL DEFAULT 'CLEAN',
        out_of_order INTEGER NOT NULL DEFAULT 0,
        inspected_at TEXT
    );
    CREATE TABLE IF NOT EXISTS room_bookings (
        id INTEGER PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        room_id INTEGER NOT NULL,
        start_at TEXT NOT NULL,
        end_at TEXT NOT NULL,
        rate_per_hour REAL,
        amount REAL,
        booked_by TEXT,
        purpose TEXT
    );
    """
    with engine.begin() as conn:
        for stmt in sql.split(";"):
            s = stmt.strip()
            if s:
                conn.execute(text(s))
        # add columns if missing (SQLite pragma)
        room_cols = {r[1] for r in conn.execute(text("PRAGMA table_info(rooms)"))}
        if "housekeeping_status" not in room_cols:
            conn.execute(text("ALTER TABLE rooms ADD COLUMN housekeeping_status TEXT DEFAULT 'CLEAN'"))
        if "out_of_order" not in room_cols:
            conn.execute(text("ALTER TABLE rooms ADD COLUMN out_of_order INTEGER DEFAULT 0"))
        if "inspected_at" not in room_cols:
            conn.execute(text("ALTER TABLE rooms ADD COLUMN inspected_at TEXT"))
        # Ensure columns exist (SQLite doesn't support IF NOT EXISTS per column, use pragma)
        cols = {r[1] for r in conn.execute(text("PRAGMA table_info(room_bookings)"))}
        if "rate_per_hour" not in cols:
            conn.execute(text("ALTER TABLE room_bookings ADD COLUMN rate_per_hour REAL"))
        if "amount" not in cols:
            conn.execute(text("ALTER TABLE room_bookings ADD COLUMN amount REAL"))


@router.get("", response_model=list[dict])
def list_rooms(tenant: str = Depends(get_tenant)):
    _ensure_tables()
    with engine.begin() as conn:
        # booked_now + current guest/checkin/checkout via correlated subqueries
        rows = conn.execute(
            text(
                """
                SELECT r.*,
                  EXISTS (
                    SELECT 1 FROM room_bookings b
                    WHERE b.tenant_id = r.tenant_id AND b.room_id = r.id
                      AND datetime(b.start_at) <= CURRENT_TIMESTAMP AND datetime(b.end_at) >= CURRENT_TIMESTAMP
                  ) AS booked_now,
                  (
                    SELECT b.booked_by FROM room_bookings b
                    WHERE b.tenant_id = r.tenant_id AND b.room_id = r.id
                      AND datetime(b.start_at) <= CURRENT_TIMESTAMP AND datetime(b.end_at) >= CURRENT_TIMESTAMP
                    ORDER BY b.start_at DESC LIMIT 1
                  ) AS current_guest,
                  (
                    SELECT b.start_at FROM room_bookings b
                    WHERE b.tenant_id = r.tenant_id AND b.room_id = r.id
                      AND datetime(b.start_at) <= CURRENT_TIMESTAMP AND datetime(b.end_at) >= CURRENT_TIMESTAMP
                    ORDER BY b.start_at DESC LIMIT 1
                  ) AS current_checkin,
                  (
                    SELECT b.end_at FROM room_bookings b
                    WHERE b.tenant_id = r.tenant_id AND b.room_id = r.id
                      AND datetime(b.start_at) <= CURRENT_TIMESTAMP AND datetime(b.end_at) >= CURRENT_TIMESTAMP
                    ORDER BY b.start_at DESC LIMIT 1
                  ) AS current_checkout
                FROM rooms r
                WHERE r.tenant_id = :t
                ORDER BY r.name
                """
            ),
            {"t": tenant},
        ).mappings().all()
    return [dict(r) for r in rows]


@router.post("", response_model=dict, dependencies=[Depends(require_role("manager"))])
def create_room(payload: Dict[str, Any], tenant: str = Depends(get_tenant)):
    _ensure_tables()
    name = (payload.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name required")
    with engine.begin() as conn:
        # unique per tenant
        exists = conn.execute(text("SELECT id FROM rooms WHERE tenant_id=:t AND name=:n"), {"t": tenant, "n": name}).first()
        if exists:
            raise HTTPException(status_code=400, detail="room already exists")
        res = conn.execute(text("INSERT INTO rooms (tenant_id, name, status) VALUES (:t,:n,'AVAILABLE')"), {"t": tenant, "n": name})
        new_id = res.lastrowid
        row = conn.execute(text("SELECT * FROM rooms WHERE id=:id"), {"id": new_id}).mappings().first()
    return dict(row)


@router.patch("/{room_id}", response_model=dict, dependencies=[Depends(require_role("manager"))])
def update_room(room_id: int, payload: Dict[str, Any], tenant: str = Depends(get_tenant)):
    _ensure_tables()
    fields: list[str] = []
    params: Dict[str, Any] = {"id": room_id, "t": tenant}

    # Load current housekeeping status to support auto-INSPECTED rule
    current_hk: Optional[str] = None
    with engine.begin() as conn:
        cur = conn.execute(
            text("SELECT housekeeping_status FROM rooms WHERE id=:id AND tenant_id=:t"),
            {"id": room_id, "t": tenant},
        ).first()
        if cur:
            current_hk = str(cur[0] or "").upper()

    if "status" in payload and payload["status"] is not None:
        fields.append("status = :st"); params["st"] = str(payload["status"]).upper()

    if "housekeeping_status" in payload and payload["housekeeping_status"] is not None:
        requested_hk = str(payload["housekeeping_status"]).upper()
        # If CLEANING -> CLEAN, auto-transition to INSPECTED and stamp inspected_at
        if requested_hk == "CLEAN" and current_hk == "CLEANING":
            fields.append("housekeeping_status = :hk"); params["hk"] = "INSPECTED"
            fields.append("inspected_at = CURRENT_TIMESTAMP")
        elif requested_hk == "INSPECTED":
            fields.append("housekeeping_status = :hk"); params["hk"] = "INSPECTED"
            fields.append("inspected_at = CURRENT_TIMESTAMP")
        else:
            fields.append("housekeeping_status = :hk"); params["hk"] = requested_hk

    if "out_of_order" in payload and payload["out_of_order"] is not None:
        fields.append("out_of_order = :ooo"); params["ooo"] = 1 if bool(payload["out_of_order"]) else 0

    if not fields:
        raise HTTPException(status_code=400, detail="no updatable fields")

    with engine.begin() as conn:
        res = conn.execute(text(f"UPDATE rooms SET {', '.join(fields)} WHERE id=:id AND tenant_id=:t"), params)
        if res.rowcount == 0:
            raise HTTPException(status_code=404, detail="room not found")
        row = conn.execute(text("SELECT * FROM rooms WHERE id=:id"), {"id": room_id}).mappings().first()
    return dict(row)


def _duration_to_minutes(preset: str) -> int:
    preset = (preset or "").lower()
    if preset in ("1h", "1", "1hour", "1 hour"): return 60
    if preset in ("2h", "2", "2hours", "2 hours"): return 120
    if preset in ("3h", "3", "3hours", "3 hours"): return 180
    if preset in ("half", "half_day", "half-day", "half day"): return 240
    if preset in ("full", "full_day", "full-day", "full day"): return 480
    if preset in ("night", "overnight", "night stay"): return 720
    return 60


@router.get("/bookings", response_model=list[dict])
def list_bookings(
    tenant: str = Depends(get_tenant),
    room_id: Optional[int] = Query(default=None),
    limit: int = Query(100, ge=1, le=500),
    date_from: Optional[str] = Query(default=None),
    date_to: Optional[str] = Query(default=None),
):
    _ensure_tables()
    where = ["tenant_id = :t"]
    params: Dict[str, Any] = {"t": tenant}
    if room_id:
        where.append("room_id = :rid"); params["rid"] = room_id
    if date_from:
        where.append("start_at >= :df"); params["df"] = date_from
    if date_to:
        where.append("start_at <= :dt"); params["dt"] = date_to
    sql = f"SELECT * FROM room_bookings WHERE {' AND '.join(where)} ORDER BY start_at DESC LIMIT :lim"
    params["lim"] = int(limit)
    with engine.begin() as conn:
        rows = conn.execute(text(sql), params).mappings().all()
    return [dict(r) for r in rows]


@router.post("/bookings", response_model=dict)
def create_booking(payload: Dict[str, Any], tenant: str = Depends(get_tenant)):
    _ensure_tables()
    try:
        room_id = int(payload.get("room_id") or 0)
    except Exception:
        room_id = 0
    if not room_id:
        raise HTTPException(status_code=400, detail="room_id required")
    start = payload.get("start_at") or datetime.utcnow().isoformat()
    try:
        start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
    except Exception:
        raise HTTPException(status_code=400, detail="invalid start_at")
    preset = payload.get("duration") or "1h"
    minutes = _duration_to_minutes(str(preset))
    end_dt = start_dt + timedelta(minutes=minutes)
    rate = payload.get("rate_per_hour")
    amount = payload.get("amount")
    if amount is None:
        try:
            rph = float(rate) if rate is not None else 0.0
        except Exception:
            rph = 0.0
        amount = round((minutes / 60.0) * rph, 2)

    with engine.begin() as conn:
        # overlap check
        overlap = conn.execute(
            text(
                """
                SELECT 1 FROM room_bookings
                WHERE tenant_id=:t AND room_id=:rid
                  AND datetime(start_at) < datetime(:end) AND datetime(end_at) > datetime(:start)
                LIMIT 1
                """
            ),
            {"t": tenant, "rid": room_id, "start": start_dt.strftime('%Y-%m-%d %H:%M:%S'), "end": end_dt.strftime('%Y-%m-%d %H:%M:%S')},
        ).first()
        if overlap:
            raise HTTPException(status_code=400, detail="overlapping booking")
        res = conn.execute(
            text(
                """
                INSERT INTO room_bookings (tenant_id, room_id, start_at, end_at, rate_per_hour, amount, booked_by, purpose)
                VALUES (:t, :rid, :start, :end, :rate, :amt, :by, :p)
                """
            ),
            {
                "t": tenant,
                "rid": room_id,
                "start": start_dt.strftime('%Y-%m-%d %H:%M:%S'),
                "end": end_dt.strftime('%Y-%m-%d %H:%M:%S'),
                "rate": rate if rate is not None else None,
                "amt": amount,
                "by": (payload.get("booked_by") or "Dispatcher"),
                "p": payload.get("purpose"),
            },
        )
        new_id = res.lastrowid
        row = conn.execute(text("SELECT * FROM room_bookings WHERE id=:id"), {"id": new_id}).mappings().first()
    return dict(row)


@router.get("/upcoming", response_model=list[dict])
def upcoming(
    tenant: str = Depends(get_tenant),
    hours: int = Query(48, ge=1, le=240),
):
    _ensure_tables()
    with engine.begin() as conn:
        rows = conn.execute(
            text(
                """
                SELECT * FROM room_bookings
                WHERE tenant_id=:t AND (
                    start_at BETWEEN CURRENT_TIMESTAMP AND datetime(CURRENT_TIMESTAMP, '+' || :h || ' hours')
                    OR end_at BETWEEN CURRENT_TIMESTAMP AND datetime(CURRENT_TIMESTAMP, '+' || :h || ' hours')
                )
                ORDER BY start_at
                """
            ),
            {"t": tenant, "h": int(hours)},
        ).mappings().all()
    return [dict(r) for r in rows]
