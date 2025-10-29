from datetime import datetime, timedelta, timezone

from sqlalchemy import text

from app.main import app
from app import deps
from app import tenant as tenant_mod
from app.db import engine
from app.api.rooms import mark_out_of_order, create_booking, mark_back_in_service


TENANT = "test_ooo"


def hdr():
    return {"X-Tenant-ID": TENANT, "X-Tenant": TENANT}


def setup_auth_overrides():
    class _U:
        id = 1
        email = "ooo@test"
        is_active = 1

    class _T:
        id = 1
        slug = TENANT

    app.dependency_overrides[deps.get_current_user] = lambda: _U()
    def _active(request):
        request.state.role = "manager"; request.state.tenant_id = 1; request.state.tenant_slug = TENANT; return _T()
    app.dependency_overrides[deps.get_active_tenant] = _active
    app.dependency_overrides[tenant_mod.get_tenant] = lambda: TENANT


def seed_room() -> int:
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS rooms (id INTEGER PRIMARY KEY, tenant_id TEXT, name TEXT, status TEXT, housekeeping_status TEXT, out_of_order INTEGER, inspected_at TEXT, base_rate REAL)"))
        conn.execute(text("DELETE FROM rooms WHERE tenant_id=:t"), {"t": TENANT})
        r = conn.execute(text("INSERT INTO rooms (tenant_id, name, status) VALUES (:t,'401','AVAILABLE')"), {"t": TENANT})
        return r.lastrowid


def test_cannot_book_ooo_and_back_in_service_respects_active():
    setup_auth_overrides()
    room_id = seed_room()

    # Mark OOO for next 3 hours
    eta = (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat().replace("+00:00", "Z")
    out = mark_out_of_order(room_id=room_id, payload={"reason": "AC broken", "eta": eta}, tenant=TENANT)  # type: ignore[arg-type]
    assert out.get("ticket") is not None

    # Try booking within 1 hour -> reject 409 out_of_order
    start = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    end = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat().replace("+00:00", "Z")
    try:
        create_booking(payload={"room_id": room_id, "purpose": "Test", "start": start, "end": end}, tenant=TENANT)  # type: ignore[arg-type]
        assert False, "Expected out_of_order rejection"
    except Exception as e:
        assert "out_of_order" in str(e)

    # Create a booking after eta -> OK
    start2 = (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat().replace("+00:00", "Z")
    end2 = (datetime.now(timezone.utc) + timedelta(hours=5)).isoformat().replace("+00:00", "Z")
    ok = create_booking(payload={"room_id": room_id, "purpose": "After", "start": start2, "end": end2}, tenant=TENANT)  # type: ignore[arg-type]
    assert ok.get("purpose") == "After"

    # Seed an active booking now to test back-in-service guard
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO room_bookings (tenant_id, room_id, start_at, end_at, amount, purpose, status, booked_by) VALUES (:t,:rid,datetime(CURRENT_TIMESTAMP,'-10 minutes'), datetime(CURRENT_TIMESTAMP,'+10 minutes'),0,'Active','RESERVED','Tester')"), {"t": TENANT, "rid": room_id})
    try:
        mark_back_in_service(room_id=room_id, tenant=TENANT)  # type: ignore[arg-type]
        assert False, "Expected active booking guard"
    except Exception as e:
        assert "active booking" in str(e)
