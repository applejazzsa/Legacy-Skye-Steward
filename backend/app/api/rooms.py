from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text

from ..db import engine
from ..tenant import get_tenant
from ..deps import require_role, get_current_user
from ..models import User  # type: ignore
from pydantic import BaseModel, Field

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
        inspected_at TEXT,
        base_rate REAL
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
        purpose TEXT,
        status TEXT NOT NULL DEFAULT 'RESERVED',
        guest_name TEXT,
        adults INTEGER,
        children INTEGER
    );
    CREATE TABLE IF NOT EXISTS housekeeping_tasks (
        id INTEGER PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        room_id INTEGER NOT NULL,
        checklist TEXT,
        status TEXT NOT NULL DEFAULT 'IN_PROGRESS',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        completed_at TEXT
    );
    CREATE TABLE IF NOT EXISTS room_audit (
        id INTEGER PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        room_id INTEGER,
        booking_id INTEGER,
        user_email TEXT,
        action TEXT NOT NULL,
        detail TEXT,
        at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS maintenance_tickets (
        id INTEGER PRIMARY KEY,
        tenant_id TEXT NOT NULL,
        room_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL DEFAULT 'OPEN',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        due_at TEXT
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
        if "base_rate" not in room_cols:
            conn.execute(text("ALTER TABLE rooms ADD COLUMN base_rate REAL"))
        # Ensure columns exist (SQLite doesn't support IF NOT EXISTS per column, use pragma)
        cols = {r[1] for r in conn.execute(text("PRAGMA table_info(room_bookings)"))}
        if "rate_per_hour" not in cols:
            conn.execute(text("ALTER TABLE room_bookings ADD COLUMN rate_per_hour REAL"))
        if "amount" not in cols:
            conn.execute(text("ALTER TABLE room_bookings ADD COLUMN amount REAL"))
        if "status" not in cols:
            conn.execute(text("ALTER TABLE room_bookings ADD COLUMN status TEXT DEFAULT 'RESERVED'"))
        if "guest_name" not in cols:
            conn.execute(text("ALTER TABLE room_bookings ADD COLUMN guest_name TEXT"))
        if "adults" not in cols:
            conn.execute(text("ALTER TABLE room_bookings ADD COLUMN adults INTEGER"))
        if "children" not in cols:
            conn.execute(text("ALTER TABLE room_bookings ADD COLUMN children INTEGER"))

        # Performance index for overlap queries
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_room_bookings_room_time ON room_bookings(room_id, start_at, end_at)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_hk_tasks_room ON housekeeping_tasks(room_id, status)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_maint_room ON maintenance_tickets(room_id, status, due_at)"))


def _audit(tenant: str, action: str, *, room_id: Optional[int] = None, booking_id: Optional[int] = None, user_email: Optional[str] = None, detail: Optional[str] = None):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO room_audit (tenant_id, room_id, booking_id, user_email, action, detail) VALUES (:t,:rid,:bid,:email,:act,:det)"),
            {"t": tenant, "rid": room_id, "bid": booking_id, "email": user_email, "act": action, "det": detail},
        )


class RoomsKpis(BaseModel):
    occupied: int = 0
    vacant: int = 0
    out_of_order: int = 0
    avg_stay_hours: float = 0
    avg_rate: float = 0
    todays_total: float = Field(0, description="Sum of amount for bookings today")
    week_total: float = Field(0, description="Sum of amount last 7 days including today")
    month_total: float = Field(0, description="Sum of amount this month")


class RecentBooking(BaseModel):
    id: int
    room_id: int
    room_no: str
    start: str
    end: str
    purpose: Optional[str] = None
    amount: float = 0
    created_by: Optional[str] = None


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
                  ) AS current_checkout,
                  (
                    SELECT b.id FROM room_bookings b
                    WHERE b.tenant_id = r.tenant_id AND b.room_id = r.id
                      AND datetime(b.start_at) <= CURRENT_TIMESTAMP AND datetime(b.end_at) >= CURRENT_TIMESTAMP
                    ORDER BY b.start_at DESC LIMIT 1
                  ) AS current_booking_id
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
    # Parameters (support new shape start/end or legacy start_at+duration)
    try:
        room_id = int(payload.get("room_id") or 0)
    except Exception:
        room_id = 0
    if not room_id:
        raise HTTPException(status_code=400, detail={"error": "room_id required"})

    start_raw = payload.get("start") or payload.get("start_at")
    end_raw = payload.get("end") or payload.get("end_at")
    duration = payload.get("duration")

    if start_raw and end_raw:
        try:
            start_dt = datetime.fromisoformat(str(start_raw).replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(str(end_raw).replace("Z", "+00:00"))
        except Exception:
            raise HTTPException(status_code=400, detail={"error": "invalid datetime"})
    elif start_raw and duration:
        try:
            start_dt = datetime.fromisoformat(str(start_raw).replace("Z", "+00:00"))
        except Exception:
            raise HTTPException(status_code=400, detail={"error": "invalid start"})
        minutes = _duration_to_minutes(str(duration))
        end_dt = start_dt + timedelta(minutes=minutes)
    else:
        raise HTTPException(status_code=400, detail={"error": "start/end or start+duration required"})

    if not (start_dt < end_dt):
        raise HTTPException(status_code=400, detail={"error": "start must be < end"})
    if (end_dt - start_dt) < timedelta(minutes=30):
        raise HTTPException(status_code=400, detail={"error": "minimum duration 30 minutes"})

    start_s = start_dt.strftime('%Y-%m-%d %H:%M:%S')
    end_s = end_dt.strftime('%Y-%m-%d %H:%M:%S')

    purpose = payload.get("purpose")
    guest_name = payload.get("guest_name")
    adults = payload.get("adults")
    children = payload.get("children")

    with engine.begin() as conn:
        # Block if room is OUT_OF_ORDER during requested range
        room_row = conn.execute(text("SELECT status FROM rooms WHERE id=:rid AND tenant_id=:t"), {"rid": room_id, "t": tenant}).mappings().first()
        if room_row and str(room_row["status"]).upper() == "OUT_OF_ORDER":
            ticket = conn.execute(text("""
                SELECT due_at FROM maintenance_tickets
                WHERE tenant_id=:t AND room_id=:rid AND status='OPEN'
                ORDER BY created_at DESC LIMIT 1
            """), {"t": tenant, "rid": room_id}).mappings().first()
            due_at = ticket["due_at"] if ticket else None
            # If due_at is null or booking starts before due_at, reject
            if due_at is None:
                raise HTTPException(status_code=409, detail={"error": "out_of_order", "until": due_at})
            try:
                due_norm = datetime.fromisoformat(str(due_at).replace('Z','+00:00')).strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                due_norm = str(due_at)
            if start_s < due_norm:
                raise HTTPException(status_code=409, detail={"error": "out_of_order", "until": due_at})
        # Find any conflicting bookings (status RESERVED or CHECKED_IN). Edge-touch is allowed.
        conflicts = conn.execute(
            text(
                """
                SELECT id, start_at, end_at, status FROM room_bookings
                WHERE tenant_id=:t AND room_id=:rid AND status IN ('RESERVED','CHECKED_IN')
                  AND datetime(start_at) < datetime(:new_end)
                  AND datetime(end_at) > datetime(:new_start)
                ORDER BY start_at
                LIMIT 5
                """
            ),
            {"t": tenant, "rid": room_id, "new_start": start_s, "new_end": end_s},
        ).mappings().all()
        if conflicts:
            raise HTTPException(status_code=409, detail={"error": "overlap", "conflicts": [dict(c) for c in conflicts]})

        # Compute amount if not provided: (rooms.base_rate or 0) * rounded_hours(0.5)
        amt = payload.get("amount")
        if amt is None:
            base_rate = conn.execute(text("SELECT base_rate FROM rooms WHERE id=:id AND tenant_id=:t"), {"id": room_id, "t": tenant}).scalar()
            try:
                base_rate_f = float(base_rate) if base_rate is not None else 0.0
            except Exception:
                base_rate_f = 0.0
            hours = (end_dt - start_dt).total_seconds() / 3600.0
            rounded = round(hours * 2) / 2.0
            computed_amount = round(base_rate_f * rounded, 2)
        else:
            try:
                computed_amount = float(amt)
            except Exception:
                computed_amount = 0.0

        # Create booking and set room status
        res = conn.execute(
            text(
                """
                INSERT INTO room_bookings (tenant_id, room_id, start_at, end_at, amount, booked_by, purpose, status, guest_name, adults, children)
                VALUES (:t, :rid, :start, :end, :amt, :by, :p, 'RESERVED', :guest, :adults, :children)
                """
            ),
            {
                "t": tenant,
                "rid": room_id,
                "start": start_s,
                "end": end_s,
                "amt": computed_amount,
                "by": (payload.get("booked_by") or "Dispatcher"),
                "p": purpose,
                "guest": guest_name,
                "adults": int(adults) if adults is not None else None,
                "children": int(children) if children is not None else None,
            },
        )
        new_id = res.lastrowid
        conn.execute(text("UPDATE rooms SET status='RESERVED' WHERE id=:id AND tenant_id=:t"), {"id": room_id, "t": tenant})
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
                WHERE tenant_id=:t AND 
                    start_at BETWEEN CURRENT_TIMESTAMP AND datetime(CURRENT_TIMESTAMP, '+' || :h || ' hours')
                ORDER BY start_at
                """
            ),
            {"t": tenant, "h": int(hours)},
        ).mappings().all()
    return [dict(r) for r in rows]


@router.get("/summary", response_model=dict)
def room_revenue_summary(tenant: str = Depends(get_tenant)):
    """
    Returns totals for day/week/month/year from room_bookings.amount.
    Uses SQLite datetime helpers on CURRENT_TIMESTAMP.
    """
    _ensure_tables()
    with engine.begin() as conn:
        day = conn.execute(text("""
            SELECT COALESCE(SUM(amount),0) FROM room_bookings
            WHERE tenant_id=:t AND date(start_at)=date(CURRENT_TIMESTAMP)
        """), {"t": tenant}).scalar() or 0.0
        week = conn.execute(text("""
            SELECT COALESCE(SUM(amount),0) FROM room_bookings
            WHERE tenant_id=:t AND date(start_at) BETWEEN date(CURRENT_TIMESTAMP,'-6 days') AND date(CURRENT_TIMESTAMP)
        """), {"t": tenant}).scalar() or 0.0
        month = conn.execute(text("""
            SELECT COALESCE(SUM(amount),0) FROM room_bookings
            WHERE tenant_id=:t AND strftime('%Y-%m', start_at)=strftime('%Y-%m', CURRENT_TIMESTAMP)
        """), {"t": tenant}).scalar() or 0.0
        year = conn.execute(text("""
            SELECT COALESCE(SUM(amount),0) FROM room_bookings
            WHERE tenant_id=:t AND strftime('%Y', start_at)=strftime('%Y', CURRENT_TIMESTAMP)
        """), {"t": tenant}).scalar() or 0.0
    return {"day": float(day), "week": float(week), "month": float(month), "year": float(year)}


@router.get("/kpis", response_model=RoomsKpis)
def rooms_kpis(
    tenant: str = Depends(get_tenant),
    time_range: Literal["last_7d", "today", "mtd"] = Query("last_7d", alias="range"),
):
    """
    Compute Rooms KPIs and revenue totals.
    Occupied = booking active now AND booking.status in ('CHECKED_IN','RESERVED') AND room.status in ('OCCUPIED','RESERVED').
    avg_rate: average hourly rate across selected range. If rate_per_hour is null, derive from amount / hours.
    """
    _ensure_tables()
    with engine.begin() as conn:
        total_rooms = conn.execute(text("SELECT COUNT(*) FROM rooms WHERE tenant_id=:t"), {"t": tenant}).scalar() or 0
        out_of_order = conn.execute(text("SELECT COUNT(*) FROM rooms WHERE tenant_id=:t AND out_of_order=1"), {"t": tenant}).scalar() or 0
        occupied = conn.execute(
            text(
                """
                SELECT COUNT(*) FROM rooms r
                WHERE r.tenant_id=:t AND r.status IN ('OCCUPIED','RESERVED') AND EXISTS (
                  SELECT 1 FROM room_bookings b
                  WHERE b.tenant_id=r.tenant_id AND b.room_id=r.id
                    AND b.status IN ('CHECKED_IN','RESERVED')
                    AND datetime(b.start_at) <= CURRENT_TIMESTAMP AND datetime(b.end_at) > CURRENT_TIMESTAMP
                )
                """
            ),
            {"t": tenant},
        ).scalar() or 0

        # Range window for averages
        if time_range == "today":
            where_window = "date(start_at)=date(CURRENT_TIMESTAMP)"
        elif time_range == "mtd":
            where_window = "strftime('%Y-%m', start_at)=strftime('%Y-%m', CURRENT_TIMESTAMP)"
        else:  # last_7d
            where_window = "date(start_at) BETWEEN date(CURRENT_TIMESTAMP,'-6 days') AND date(CURRENT_TIMESTAMP)"

        # Average stay (hours) and avg rate (hourly); totals for day/week/month
        avg_stay_hours = conn.execute(
            text(
                f"""
                SELECT COALESCE(AVG((julianday(end_at) - julianday(start_at)) * 24.0),0)
                FROM room_bookings WHERE tenant_id=:t AND {where_window}
                """
            ),
            {"t": tenant},
        ).scalar() or 0.0

        # Derive per-booking hourly rate when missing
        avg_rate = conn.execute(
            text(
                f"""
                SELECT COALESCE(AVG(
                    CASE
                      WHEN rate_per_hour IS NOT NULL THEN rate_per_hour
                      WHEN amount IS NOT NULL AND (julianday(end_at) - julianday(start_at)) > 0
                        THEN amount / ((julianday(end_at) - julianday(start_at)) * 24.0)
                      ELSE NULL
                    END
                ),0)
                FROM room_bookings WHERE tenant_id=:t AND {where_window}
                """
            ),
            {"t": tenant},
        ).scalar() or 0.0

        todays_total = conn.execute(text("""
            SELECT COALESCE(SUM(amount),0) FROM room_bookings
            WHERE tenant_id=:t AND date(start_at)=date(CURRENT_TIMESTAMP)
        """), {"t": tenant}).scalar() or 0.0
        week_total = conn.execute(text("""
            SELECT COALESCE(SUM(amount),0) FROM room_bookings
            WHERE tenant_id=:t AND date(start_at) BETWEEN date(CURRENT_TIMESTAMP,'-6 days') AND date(CURRENT_TIMESTAMP)
        """), {"t": tenant}).scalar() or 0.0
        month_total = conn.execute(text("""
            SELECT COALESCE(SUM(amount),0) FROM room_bookings
            WHERE tenant_id=:t AND strftime('%Y-%m', start_at)=strftime('%Y-%m', CURRENT_TIMESTAMP)
        """), {"t": tenant}).scalar() or 0.0

    vacant = max(0, int(total_rooms) - int(occupied) - int(out_of_order))
    return RoomsKpis(
        occupied=int(occupied),
        vacant=int(vacant),
        out_of_order=int(out_of_order),
        avg_stay_hours=float(avg_stay_hours),
        avg_rate=float(avg_rate),
        todays_total=float(todays_total),
        week_total=float(week_total),
        month_total=float(month_total),
    )


@router.get("/bookings/recent", response_model=list[RecentBooking])
def recent_bookings(tenant: str = Depends(get_tenant), limit: int = Query(20, ge=1, le=200)):
    _ensure_tables()
    with engine.begin() as conn:
        rows = conn.execute(
            text(
                """
                SELECT b.id, b.room_id, COALESCE(r.name, '#'||b.room_id) AS room_no,
                       b.start_at AS start, b.end_at AS end, b.purpose, COALESCE(b.amount,0) AS amount,
                       b.booked_by AS created_by
                FROM room_bookings b
                LEFT JOIN rooms r ON r.id=b.room_id AND r.tenant_id=b.tenant_id
                WHERE b.tenant_id=:t
                ORDER BY datetime(b.start_at) DESC
                LIMIT :lim
                """
            ),
            {"t": tenant, "lim": int(limit)},
        ).mappings().all()
    return [RecentBooking(**dict(r)) for r in rows]


@router.get("/bookings/upcoming", response_model=list[dict])
def upcoming_bookings_alias(tenant: str = Depends(get_tenant), hours: int = Query(48, ge=1, le=240)):
    """Alias that matches requested path: /rooms/bookings/upcoming?hours=.."""
    return upcoming(tenant=tenant, hours=hours)


@router.post("/bookings/{booking_id}/check-in", response_model=dict)
def booking_check_in(booking_id: int, tenant: str = Depends(get_tenant), user: User = Depends(get_current_user)):
    _ensure_tables()
    now = datetime.utcnow()
    with engine.begin() as conn:
        row = conn.execute(text("""
            SELECT b.*, r.status AS room_status FROM room_bookings b
            JOIN rooms r ON r.id=b.room_id AND r.tenant_id=b.tenant_id
            WHERE b.id=:id AND b.tenant_id=:t
        """), {"id": booking_id, "t": tenant}).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="booking not found")
        if str(row["room_status"]).upper() in ("OUT_OF_ORDER", "CLEANING"):
            raise HTTPException(status_code=400, detail="room not available for check-in")
        if str(row["status"]).upper() != "RESERVED":
            raise HTTPException(status_code=400, detail="booking not in RESERVED status")
        # window: now within [start-2h, end]
        start_dt = datetime.fromisoformat(str(row["start_at"]))
        end_dt = datetime.fromisoformat(str(row["end_at"]))
        if not (start_dt - timedelta(hours=2) <= now <= end_dt):
            raise HTTPException(status_code=400, detail="outside check-in window")
        conn.execute(text("UPDATE room_bookings SET status='CHECKED_IN' WHERE id=:id"), {"id": booking_id})
        conn.execute(text("UPDATE rooms SET status='OCCUPIED' WHERE id=:rid AND tenant_id=:t"), {"rid": int(row["room_id"]), "t": tenant})
    _audit(tenant, "check_in", room_id=int(row["room_id"]), booking_id=booking_id, user_email=getattr(user, "email", None))
    with engine.begin() as conn:
        out = conn.execute(text("SELECT * FROM room_bookings WHERE id=:id"), {"id": booking_id}).mappings().first()
    return dict(out)


@router.post("/bookings/{booking_id}/check-out", response_model=dict)
def booking_check_out(booking_id: int, tenant: str = Depends(get_tenant), user: User = Depends(get_current_user)):
    _ensure_tables()
    with engine.begin() as conn:
        row = conn.execute(text("""
            SELECT b.*, r.status AS room_status FROM room_bookings b
            JOIN rooms r ON r.id=b.room_id AND r.tenant_id=b.tenant_id
            WHERE b.id=:id AND b.tenant_id=:t
        """), {"id": booking_id, "t": tenant}).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="booking not found")
        if str(row["status"]).upper() != "CHECKED_IN":
            raise HTTPException(status_code=400, detail="booking not checked in")
        conn.execute(text("UPDATE room_bookings SET status='CHECKED_OUT' WHERE id=:id"), {"id": booking_id})
        conn.execute(text("UPDATE rooms SET status='CLEANING', housekeeping_status='CLEANING' WHERE id=:rid AND tenant_id=:t"), {"rid": int(row["room_id"]), "t": tenant})
        # Create housekeeping task
        checklist = "Make bed\nSanitize\nAmenities"
        res = conn.execute(text("INSERT INTO housekeeping_tasks (tenant_id, room_id, checklist, status) VALUES (:t,:rid,:cl,'IN_PROGRESS')"), {"t": tenant, "rid": int(row["room_id"]), "cl": checklist})
        task_id = res.lastrowid
    _audit(tenant, "check_out", room_id=int(row["room_id"]), booking_id=booking_id, user_email=getattr(user, "email", None))
    with engine.begin() as conn:
        out = conn.execute(text("SELECT * FROM housekeeping_tasks WHERE id=:id"), {"id": task_id}).mappings().first()
    return {"booking_id": booking_id, "housekeeping_task": dict(out)}


@router.post("/housekeeping/tasks/{task_id}/complete", response_model=dict)
def housekeeping_complete(task_id: int, tenant: str = Depends(get_tenant), user: User = Depends(get_current_user)):
    _ensure_tables()
    with engine.begin() as conn:
        task = conn.execute(text("SELECT * FROM housekeeping_tasks WHERE id=:id AND tenant_id=:t"), {"id": task_id, "t": tenant}).mappings().first()
        if not task:
            raise HTTPException(status_code=404, detail="task not found")
        conn.execute(text("UPDATE housekeeping_tasks SET status='CLEAN', completed_at=CURRENT_TIMESTAMP WHERE id=:id"), {"id": task_id})
        conn.execute(text("UPDATE rooms SET status='AVAILABLE', housekeeping_status='CLEAN' WHERE id=:rid AND tenant_id=:t"), {"rid": int(task["room_id"]), "t": tenant})
    _audit(tenant, "housekeeping_complete", room_id=int(task["room_id"]), user_email=getattr(user, "email", None))
    with engine.begin() as conn:
        out = conn.execute(text("SELECT * FROM housekeeping_tasks WHERE id=:id"), {"id": task_id}).mappings().first()
    return dict(out)


@router.get("/housekeeping/tasks", response_model=list[dict])
def list_housekeeping_tasks(tenant: str = Depends(get_tenant), room_id: Optional[int] = Query(default=None), status: Optional[str] = Query(default=None)):
    _ensure_tables()
    where = ["tenant_id=:t"]
    params: Dict[str, Any] = {"t": tenant}
    if room_id:
        where.append("room_id=:rid"); params["rid"] = room_id
    if status:
        where.append("status=:st"); params["st"] = status
    sql = f"SELECT * FROM housekeeping_tasks WHERE {' AND '.join(where)} ORDER BY created_at DESC"
    with engine.begin() as conn:
        rows = conn.execute(text(sql), params).mappings().all()
    return [dict(r) for r in rows]


@router.post("/{room_id}/out-of-order", response_model=dict, dependencies=[Depends(require_role("manager"))])
def mark_out_of_order(room_id: int, payload: Dict[str, Any], tenant: str = Depends(get_tenant), user: User = Depends(get_current_user)):
    """
    Sets room.status=OUT_OF_ORDER and creates a maintenance ticket.
    Body: {reason, eta}
    """
    _ensure_tables()
    reason = (payload.get("reason") or "General").strip()
    eta = payload.get("eta")
    with engine.begin() as conn:
        res = conn.execute(text("UPDATE rooms SET status='OUT_OF_ORDER', out_of_order=1 WHERE id=:id AND tenant_id=:t"), {"id": room_id, "t": tenant})
        if res.rowcount == 0:
            raise HTTPException(status_code=404, detail="room not found")
        tic = conn.execute(text("""
            INSERT INTO maintenance_tickets (tenant_id, room_id, category, description, status, due_at)
            VALUES (:t,:rid,'General',:desc,'OPEN',:due)
        """), {"t": tenant, "rid": room_id, "desc": reason, "due": eta}).lastrowid
        ticket = conn.execute(text("SELECT * FROM maintenance_tickets WHERE id=:id"), {"id": tic}).mappings().first()
    _audit(tenant, "room_out_of_order", room_id=room_id, user_email=getattr(user, "email", None), detail=reason)
    return {"room_id": room_id, "ticket": dict(ticket)}


@router.post("/{room_id}/back-in-service", response_model=dict, dependencies=[Depends(require_role("manager"))])
def mark_back_in_service(room_id: int, tenant: str = Depends(get_tenant), user: User = Depends(get_current_user)):
    """
    Sets room.status=AVAILABLE if there is no active booking now. Closes open maintenance tickets.
    """
    _ensure_tables()
    with engine.begin() as conn:
        # active booking now?
        active = conn.execute(text("""
            SELECT 1 FROM room_bookings WHERE tenant_id=:t AND room_id=:rid
            AND datetime(start_at) <= CURRENT_TIMESTAMP AND datetime(end_at) >= CURRENT_TIMESTAMP
            LIMIT 1
        """), {"t": tenant, "rid": room_id}).first()
        if active:
            raise HTTPException(status_code=400, detail="active booking prevents service")
        res = conn.execute(text("UPDATE rooms SET status='AVAILABLE', out_of_order=0 WHERE id=:id AND tenant_id=:t"), {"id": room_id, "t": tenant})
        if res.rowcount == 0:
            raise HTTPException(status_code=404, detail="room not found")
        conn.execute(text("UPDATE maintenance_tickets SET status='CLOSED' WHERE tenant_id=:t AND room_id=:rid AND status='OPEN'"), {"t": tenant, "rid": room_id})
        room = conn.execute(text("SELECT * FROM rooms WHERE id=:id"), {"id": room_id}).mappings().first()
    _audit(tenant, "room_back_in_service", room_id=room_id, user_email=getattr(user, "email", None))
    return dict(room)

@router.post("/bookings/availability", response_model=dict)
def check_availability(payload: Dict[str, Any], tenant: str = Depends(get_tenant)):
    """
    Pre-check availability for a proposed booking.
    Body: { room_id, start, end }
    Returns: { available: bool, conflicts?: [...], reason?: string, until?: string }
    """
    _ensure_tables()
    try:
        room_id = int(payload.get("room_id") or 0)
    except Exception:
        room_id = 0
    if not room_id:
        raise HTTPException(status_code=400, detail={"error": "room_id required"})
    start_raw = payload.get("start") or payload.get("start_at")
    end_raw = payload.get("end") or payload.get("end_at")
    if not (start_raw and end_raw):
        raise HTTPException(status_code=400, detail={"error": "start and end required"})
    try:
        start_dt = datetime.fromisoformat(str(start_raw).replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(str(end_raw).replace("Z", "+00:00"))
    except Exception:
        raise HTTPException(status_code=400, detail={"error": "invalid datetime"})
    if not (start_dt < end_dt):
        return {"available": False, "reason": "end_before_start"}
    if (end_dt - start_dt) < timedelta(minutes=30):
        return {"available": False, "reason": "short_duration"}

    start_s = start_dt.strftime('%Y-%m-%d %H:%M:%S')
    end_s = end_dt.strftime('%Y-%m-%d %H:%M:%S')

    with engine.begin() as conn:
        # OOO rule
        room_row = conn.execute(text("SELECT status FROM rooms WHERE id=:rid AND tenant_id=:t"), {"rid": room_id, "t": tenant}).mappings().first()
        if room_row and str(room_row["status"]).upper() == "OUT_OF_ORDER":
            ticket = conn.execute(text("""
                SELECT due_at FROM maintenance_tickets
                WHERE tenant_id=:t AND room_id=:rid AND status='OPEN'
                ORDER BY created_at DESC LIMIT 1
            """), {"t": tenant, "rid": room_id}).mappings().first()
            due_at = ticket["due_at"] if ticket else None
            if due_at is None:
                return {"available": False, "reason": "out_of_order"}
            try:
                due_norm = datetime.fromisoformat(str(due_at).replace('Z','+00:00')).strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                due_norm = str(due_at)
            if start_s < due_norm:
                return {"available": False, "reason": "out_of_order", "until": due_at}

        conflicts = conn.execute(text("""
            SELECT id, start_at, end_at, status FROM room_bookings
            WHERE tenant_id=:t AND room_id=:rid AND status IN ('RESERVED','CHECKED_IN')
              AND datetime(start_at) < datetime(:new_end)
              AND datetime(end_at) > datetime(:new_start)
            ORDER BY start_at LIMIT 3
        """), {"t": tenant, "rid": room_id, "new_start": start_s, "new_end": end_s}).mappings().all()
    if conflicts:
        return {"available": False, "reason": "overlap", "conflicts": [dict(c) for c in conflicts]}
    return {"available": True}
