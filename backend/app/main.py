"""FastAPI application entry point."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import analytics, crud
from .config import get_cors_origins
from .deps import get_db
from .schemas import HandoverCreate, HandoverRead, KPISummary

app = FastAPI(
    title="Legacy Skye Steward API",
    version="1.0.0",
    openapi_tags=[
        {"name": "Health", "description": "Health checks for uptime monitoring."},
        {
            "name": "Handovers",
            "description": "Create and query hospitality handover information.",
        },
        {
            "name": "Analytics",
            "description": "Aggregated insights for leadership dashboards.",
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    """Return a simple readiness check."""

    now = datetime.now(timezone.utc)
    return {
        "status": "healthy",
        "time": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }


@app.post("/api/handover", response_model=HandoverRead, tags=["Handovers"])
def create_handover(
    payload: HandoverCreate,
    db: Annotated[Session, Depends(get_db)],
) -> HandoverRead:
    """Create a new handover entry."""

    handover = crud.create_handover(db, payload)
    return HandoverRead.model_validate(handover)


@app.get("/api/handover", response_model=list[HandoverRead], tags=["Handovers"])
def list_handover(
    *,
    outlet: str | None = None,
    start_date: str | None = Query(None, description="Inclusive ISO8601 start date."),
    end_date: str | None = Query(None, description="Inclusive ISO8601 end date."),
    db: Annotated[Session, Depends(get_db)],
) -> list[HandoverRead]:
    """List handovers optionally filtered by outlet and date range."""

    start = analytics.parse_iso_datetime(start_date)
    end = analytics.parse_iso_datetime(end_date)
    if start and end and start > end:
        raise HTTPException(status_code=400, detail="start_date cannot be after end_date")

    handovers = crud.list_handovers(db, outlet=outlet, start_date=start, end_date=end)
    return [HandoverRead.model_validate(h) for h in handovers]


@app.get("/api/analytics/top-items", tags=["Analytics"])
def top_items(
    limit: int = Query(5, ge=1, le=50),
    outlet: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    db: Annotated[Session, Depends(get_db)],
) -> list[dict[str, str | int]]:
    """Return the most popular top sales items for the period."""

    start, end = analytics.normalize_window(
        analytics.parse_iso_datetime(start_date),
        analytics.parse_iso_datetime(end_date),
    )
    return analytics.top_items(db, start=start, end=end, outlet=outlet, limit=limit)


@app.get("/api/analytics/staff-praise", tags=["Analytics"])
def staff_praise(
    limit: int = Query(5, ge=1, le=50),
    outlet: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    db: Annotated[Session, Depends(get_db)],
) -> list[dict[str, str | int]]:
    """Return the staff praise leaderboard."""

    start, end = analytics.normalize_window(
        analytics.parse_iso_datetime(start_date),
        analytics.parse_iso_datetime(end_date),
    )
    return analytics.staff_praise(db, start=start, end=end, outlet=outlet, limit=limit)


@app.get("/api/analytics/kpi-summary", response_model=KPISummary, tags=["Analytics"])
def kpi_summary(
    target: float = Query(..., description="Revenue target for the window."),
    outlet: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    db: Annotated[Session, Depends(get_db)],
) -> KPISummary:
    """Return KPI summary for the requested period."""

    start, end = analytics.normalize_window(
        analytics.parse_iso_datetime(start_date),
        analytics.parse_iso_datetime(end_date),
    )
    summary = analytics.kpi_summary(
        db,
        start=start,
        end=end,
        outlet=outlet,
        target=target,
    )
    # Ensure datetime values serialize with trailing Z.
    summary["window"]["start"] = summary["window"]["start"].isoformat().replace("+00:00", "Z")
    summary["window"]["end"] = summary["window"]["end"].isoformat().replace("+00:00", "Z")
    return KPISummary.model_validate(summary)


__all__ = ["app"]
