from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app import deps
from app import tenant as tenant_mod
from app.db import engine
from fastapi import Request


TENANT = "test_booking_rules"


def hdr():
    return {"X-Tenant-ID": TENANT, "X-Tenant": TENANT}


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def setup_auth_overrides():
    class _U:
        id = 1
        email = "tester@example.com"
        is_active = 1

    class _T:
        id = 1
        slug = TENANT

    def _fake_user():
        return _U()

    def _fake_active_tenant(request: Request):
        request.state.role = "owner"
        request.state.tenant_id = 1
        request.state.tenant_slug = TENANT
        return _T()

    app.dependency_overrides[deps.get_current_user] = _fake_user
    app.dependency_overrides[deps.get_active_tenant] = _fake_active_tenant
    app.dependency_overrides[tenant_mod.get_tenant] = lambda: TENANT


def seed_room(base_rate: float = 100.0) -> int:
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS rooms (id INTEGER PRIMARY KEY, tenant_id TEXT, name TEXT, status TEXT, housekeeping_status TEXT, out_of_order INTEGER, inspected_at TEXT, base_rate REAL)"))
        conn.execute(text("CREATE TABLE IF NOT EXISTS room_bookings (id INTEGER PRIMARY KEY, tenant_id TEXT, room_id INTEGER, start_at TEXT, end_at TEXT, rate_per_hour REAL, amount REAL, booked_by TEXT, purpose TEXT, status TEXT, guest_name TEXT, adults INTEGER, children INTEGER)"))
        conn.execute(text("DELETE FROM room_bookings WHERE tenant_id=:t"), {"t": TENANT})
        conn.execute(text("DELETE FROM rooms WHERE tenant_id=:t"), {"t": TENANT})
        res = conn.execute(text("INSERT INTO rooms (tenant_id, name, status, base_rate) VALUES (:t,'201','AVAILABLE',:r)"), {"t": TENANT, "r": base_rate})
        return res.lastrowid


def test_overlap_and_edge_touch_and_amount_compute():
    setup_auth_overrides()
    client = TestClient(app)

    room_id = seed_room(120.0)
    now = datetime.now(timezone.utc)

    # Insert an existing booking: 10:00 - 12:00
    from app.api.rooms import create_booking
    data1 = create_booking(payload={"room_id": room_id, "purpose": "A", "start": iso(now.replace(minute=0, second=0, microsecond=0)), "end": iso(now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=2)), "amount": 200}, tenant=TENANT)  # type: ignore[arg-type]
    assert (data1.get("purpose") or "") == "A"

    # Exact overlap (10:30 - 11:30) should be rejected (409)
    try:
        create_booking(payload={"room_id": room_id, "purpose": "B", "start": iso(now.replace(minute=30, second=0, microsecond=0)), "end": iso(now.replace(minute=30, second=0, microsecond=0) + timedelta(hours=1))}, tenant=TENANT)  # type: ignore[arg-type]
        assert False, "Expected overlap rejection"
    except Exception as e:
        assert "overlap" in str(e)

    # Edge-touch (end == start) should be allowed: new 12:00 - 13:00
    start_edge = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=2)
    ok2 = create_booking(payload={"room_id": room_id, "purpose": "C", "start": iso(start_edge), "end": iso(start_edge + timedelta(hours=1))}, tenant=TENANT)  # type: ignore[arg-type]
    assert ok2.get("purpose") == "C"

    # Amount compute: if amount omitted, it uses base_rate * rounded_hours(0.5)
    # Create a 45-minute booking -> 0.5h rounded from 0.75? Wait 45m is 0.75h, nearest 0.5 is 1.0; but we used round to nearest 0.5 => 1.0
    # So expected is 120 * 1.0 = 120
    s3 = start_edge + timedelta(hours=2)
    e3 = s3 + timedelta(minutes=45)
    data3 = create_booking(payload={"room_id": room_id, "purpose": "D", "start": iso(s3), "end": iso(e3)}, tenant=TENANT)  # type: ignore[arg-type]
    amt = float(data3.get("amount") or 0)
    assert amt == 120.0
