from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "ok"

def test_ping():
    r = client.get("/api/ping")
    assert r.status_code == 200
    body = r.json()
    assert body.get("ok") is True
    assert body.get("service") == "steward"

def test_create_and_list_handover():
    payload = {
        "outlet": "Cafe Grill",
        "shift": "AM",
        "period": "BREAKFAST",
        "bookings": 10,
        "walk_ins": 5,
        "covers": 30,
        "food_revenue": 12750.0,
        "beverage_revenue": 840.0,
        "top_sales": ["Beef Fillet", "Sustainable Hake"]
    }
    r = client.post("/api/handover", json=payload)
    assert r.status_code == 200
    saved = r.json()
    assert saved["id"] >= 1
    assert saved["outlet"] == "Cafe Grill"

    r2 = client.get("/api/handovers?outlet=Cafe Grill&period=BREAKFAST&shift=AM")
    assert r2.status_code == 200
    items = r2.json()
    assert len(items) >= 1
    assert items[0]["outlet"] == "Cafe Grill"

def test_incident_lifecycle():
    create = {
        "outlet": "Azure",
        "description": "Child choked due to unblended veg; action required.",
        "severity": "HIGH",
        "owner": "Duty Manager",
        "guest_reference": "Room 209"
    }
    r = client.post("/api/incidents", json=create)
    assert r.status_code == 200
    inc = r.json()
    assert inc["status"] == "OPEN"
    inc_id = inc["id"]

    # list open
    r2 = client.get("/api/incidents?status=OPEN&outlet=Azure")
    assert r2.status_code == 200
    items = r2.json()
    assert any(i["id"] == inc_id for i in items)

    # resolve
    r3 = client.post(f"/api/incidents/{inc_id}/resolve", params={"action_taken": "Veg blended; staff briefed."})
    assert r3.status_code == 200
    resolved = r3.json()
    assert resolved["status"] == "RESOLVED"
    assert "Veg blended" in resolved["action_taken"]

def test_guest_notes_flow():
    note = {
        "outlet": "Leopard Bar",
        "guest_name": "Private",
        "room_number": None,
        "occasion": "Anniversary",
        "note": "Loved the High Tea and cocktails; praised Nolundi.",
        "sentiment": "VERY_HAPPY",
        "staff_praised": "Nolundi"
    }
    r = client.post("/api/guest-notes", json=note)
    assert r.status_code == 200
    saved = r.json()
    assert saved["id"] >= 1

    r2 = client.get("/api/guest-notes?outlet=Leopard Bar&sentiment=VERY_HAPPY")
    assert r2.status_code == 200
    items = r2.json()
    assert len(items) >= 1
    assert items[0]["staff_praised"] == "Nolundi"
