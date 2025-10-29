from datetime import datetime, timedelta, timezone

from sqlalchemy import text

from app.main import app
from app import deps
from app import tenant as tenant_mod
from app.db import engine
from app.api.rooms import booking_check_in, booking_check_out, housekeeping_complete


TENANT = "test_state"


def hdr():
    return {"X-Tenant-ID": TENANT, "X-Tenant": TENANT}


def setup_auth_overrides():
    class _U:
        id = 1
        email = "state@test"
        is_active = 1

    class _T:
        id = 1
        slug = TENANT

    app.dependency_overrides[deps.get_current_user] = lambda: _U()
    def _active(request):
        request.state.role = "owner"; request.state.tenant_id = 1; request.state.tenant_slug = TENANT; return _T()
    app.dependency_overrides[deps.get_active_tenant] = _active
    app.dependency_overrides[tenant_mod.get_tenant] = lambda: TENANT


def seed_room_and_booking():
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS rooms (id INTEGER PRIMARY KEY, tenant_id TEXT, name TEXT, status TEXT, housekeeping_status TEXT, out_of_order INTEGER, inspected_at TEXT, base_rate REAL)"))
        conn.execute(text("CREATE TABLE IF NOT EXISTS room_bookings (id INTEGER PRIMARY KEY, tenant_id TEXT, room_id INTEGER, start_at TEXT, end_at TEXT, amount REAL, purpose TEXT, status TEXT, booked_by TEXT)"))
        conn.execute(text("DELETE FROM room_bookings WHERE tenant_id=:t"), {"t": TENANT})
        conn.execute(text("DELETE FROM rooms WHERE tenant_id=:t"), {"t": TENANT})
        r = conn.execute(text("INSERT INTO rooms (tenant_id, name, status, housekeeping_status) VALUES (:t,'301','CLEANING','CLEANING')"), {"t": TENANT})
        room_id = r.lastrowid
        start = (now - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        end = (now + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        b = conn.execute(text("INSERT INTO room_bookings (tenant_id, room_id, start_at, end_at, amount, purpose, status, booked_by) VALUES (:t,:rid,:s,:e,0,'Test','RESERVED','Tester')"), {"t": TENANT, "rid": room_id, "s": start, "e": end})
        return room_id, b.lastrowid


def test_transitions_and_guards():
    setup_auth_overrides()
    room_id, booking_id = seed_room_and_booking()

    # Guard: room CLEANING blocks check-in
    try:
        booking_check_in(booking_id=booking_id, tenant=TENANT)  # type: ignore[arg-type]
        assert False, "Expected guard failure"
    except Exception as e:
        # HTTPException
        assert "room not available" in str(e).lower() or "400" in str(e)

    # Make room AVAILABLE and check-in within window
    with engine.begin() as conn:
        conn.execute(text("UPDATE rooms SET status='AVAILABLE', housekeeping_status='CLEAN' WHERE id=:rid AND tenant_id=:t"), {"rid": room_id, "t": TENANT})
    out = booking_check_in(booking_id=booking_id, tenant=TENANT)  # type: ignore[arg-type]
    assert out.get("status", "").upper() == "CHECKED_IN"
    # Room should be OCCUPIED
    with engine.begin() as conn:
        st = conn.execute(text("SELECT status FROM rooms WHERE id=:rid"), {"rid": room_id}).scalar()
        assert str(st).upper() == 'OCCUPIED'

    # Check-out: should create HK task and set CLEANING
    body = booking_check_out(booking_id=booking_id, tenant=TENANT)  # type: ignore[arg-type]
    task = body.get("housekeeping_task") or {}
    assert (task.get("status") or '').upper() == 'IN_PROGRESS'
    tid = task.get("id")
    with engine.begin() as conn:
        st2 = conn.execute(text("SELECT status FROM rooms WHERE id=:rid"), {"rid": room_id}).scalar()
        assert str(st2).upper() == 'CLEANING'

    # Complete housekeeping task: room AVAILABLE and task CLEAN
    done = housekeeping_complete(task_id=tid, tenant=TENANT)  # type: ignore[arg-type]
    assert (done.get("status") or '').upper() == 'CLEAN'
    with engine.begin() as conn:
        st3 = conn.execute(text("SELECT status FROM rooms WHERE id=:rid"), {"rid": room_id}).scalar()
        assert str(st3).upper() == 'AVAILABLE'
