from __future__ import annotations

import os
from datetime import datetime, timezone

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert "time" in payload


def test_create_and_list_handover(client: TestClient) -> None:
    iso_date = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    payload = {
        "outlet": "Main Restaurant",
        "date": iso_date,
        "shift": "PM",
        "period": "DINNER",
        "bookings": 12,
        "walk_ins": 8,
        "covers": 60,
        "food_revenue": 4200.50,
        "beverage_revenue": 1800.25,
        "top_sales": ["Chef's Special", "Signature Cocktail"],
    }

    create_response = client.post("/api/handover", json=payload)
    assert create_response.status_code == 200
    created = create_response.json()
    for key, value in payload.items():
        assert created[key] == value

    list_response = client.get("/api/handover")
    assert list_response.status_code == 200
    body = list_response.json()
    assert isinstance(body, list)
    assert len(body) >= 1


def test_kpi_summary(client: TestClient) -> None:
    response = client.get("/api/analytics/kpi-summary", params={"target": 1000})
    assert response.status_code == 200
    summary = response.json()
    assert set(summary.keys()) == {"window", "current", "previous", "change_pct", "target"}
    for key in ["covers", "food_revenue", "beverage_revenue", "total_revenue", "avg_check"]:
        assert key in summary["current"]
        assert key in summary["previous"]
    assert set(summary["change_pct"].keys()) == {"covers", "total_revenue", "avg_check"}
    assert set(summary["target"].keys()) == {"total_revenue_target", "achievement_pct"}
