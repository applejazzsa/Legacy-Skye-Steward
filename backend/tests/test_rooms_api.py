# feat(tests): add KPI and upcoming window tests for rooms
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.main import app
from app import deps
from app import tenant as tenant_mod
from app.api.rooms import rooms_kpis, upcoming
from app.db import engine
from sqlalchemy import text



TENANT = "test_kpis"


def hdr():
    return {"X-Tenant-ID": TENANT, "X-Tenant": TENANT}


def iso(dt: datetime) -> str:
    # Return ISO string with Z
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def test_kpis_and_upcoming():
    # Override auth/tenant for tests
    class _U:
        id = 1
        email = "tester@example.com"
        is_active = 1

    class _T:
        id = 1
        slug = TENANT

    def _fake_user():
        return _U()

    def _fake_active_tenant(request):
        # mimic set state used by require_role
        request.state.role = "owner"
        request.state.tenant_id = 1
        request.state.tenant_slug = TENANT
        return _T()

    app.dependency_overrides[deps.get_current_user] = _fake_user
    app.dependency_overrides[deps.get_active_tenant] = _fake_active_tenant
    app.dependency_overrides[tenant_mod.get_tenant] = lambda: TENANT

    local_client = TestClient(app)

    # Seed rooms directly (bypass RBAC on create_room)
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS rooms (
              id INTEGER PRIMARY KEY,
              tenant_id TEXT NOT NULL,
              name TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'AVAILABLE',
              housekeeping_status TEXT NOT NULL DEFAULT 'CLEAN',
              out_of_order INTEGER NOT NULL DEFAULT 0,
              inspected_at TEXT
            )
        """))
        # insert two rooms for tenant
        conn.execute(text("DELETE FROM rooms WHERE tenant_id=:t"), {"t": TENANT})
        res1 = conn.execute(text("INSERT INTO rooms (tenant_id, name, status, out_of_order) VALUES (:t,'101','OCCUPIED',0)"), {"t": TENANT})
        res2 = conn.execute(text("INSERT INTO rooms (tenant_id, name, status, out_of_order) VALUES (:t,'102','AVAILABLE',1)"), {"t": TENANT})
        room1_id = res1.lastrowid
        room2_id = res2.lastrowid

    now = datetime.now(timezone.utc)
    # Seed bookings directly
    with engine.begin() as conn:
        conn.execute(text("""
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
              status TEXT DEFAULT 'RESERVED'
            )
        """))
        # ensure status column exists if table pre-created without it
        cols = [row[1] for row in conn.execute(text("PRAGMA table_info(room_bookings)"))]
        if "status" not in cols:
            conn.execute(text("ALTER TABLE room_bookings ADD COLUMN status TEXT DEFAULT 'RESERVED'"))
        # Active now: start -30m, end +30m
        start1 = (now - timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
        end1 = (now + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(text("""
            INSERT INTO room_bookings (tenant_id, room_id, start_at, end_at, amount, booked_by, purpose, status)
            VALUES (:t,:rid,:s,:e,100,'Tester','Stay','RESERVED')
        """), {"t": TENANT, "rid": room1_id, "s": start1, "e": end1})
        # Last 7d (2 days ago)
        start2 = (now - timedelta(days=2, hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        end2 = (now - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(text("""
            INSERT INTO room_bookings (tenant_id, room_id, start_at, end_at, amount, booked_by, purpose, status)
            VALUES (:t,:rid,:s,:e,50,'Tester','Meeting','RESERVED')
        """), {"t": TENANT, "rid": room1_id, "s": start2, "e": end2})
        # Upcoming +2h
        start3 = (now + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
        end3 = (now + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')
        conn.execute(text("""
            INSERT INTO room_bookings (tenant_id, room_id, start_at, end_at, amount, booked_by, purpose, status)
            VALUES (:t,:rid,:s,:e,75,'Tester','Upcoming','RESERVED')
        """), {"t": TENANT, "rid": room1_id, "s": start3, "e": end3})

    # KPIs (last 7d) via direct function call (unit-style)
    data = rooms_kpis(tenant=TENANT, time_range="last_7d")
    # occupied=1 (room1), out_of_order=1 (room2), vacant=total(2)-1-1=0
    assert data.occupied == 1
    assert data.out_of_order == 1
    assert data.vacant == 0
    # todays_total should be 100 (b1), week_total >= 150, month_total >= week_total
    assert data.todays_total >= 100
    assert data.week_total >= 150
    assert data.month_total >= data.week_total

    # Upcoming window tests via direct function
    up1 = upcoming(tenant=TENANT, hours=1)
    assert isinstance(up1, list)
    assert len(up1) == 0
    up2 = upcoming(tenant=TENANT, hours=3)
    assert any((x.get("purpose") if isinstance(x, dict) else x.purpose) == "Upcoming" for x in up2)
