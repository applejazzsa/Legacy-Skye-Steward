from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Handover, Incident, CapaAction
from ..tenant import get_tenant

router = APIRouter(prefix="/api/digest", tags=["digest"])


@router.get("/run-of-day", response_model=dict)
def run_of_day(tenant: str = Depends(get_tenant), db: Session = Depends(get_db)):
    today = date.today()
    tomorrow = today + timedelta(days=1)

    handovers = (
        db.query(Handover)
        .filter(Handover.tenant_id == tenant)
        .order_by(Handover.date.desc())
        .limit(5)
        .all()
    )

    open_incidents = (
        db.query(Incident)
        .filter(Incident.tenant_id == tenant, Incident.status != "CLOSED")
        .order_by(Incident.created_at.desc())
        .limit(10)
        .all()
    )

    due_actions = (
        db.query(CapaAction)
        .filter(CapaAction.tenant_id == tenant, CapaAction.status != "DONE")
        .order_by(CapaAction.due_date.asc().nulls_last())
        .limit(10)
        .all()
    )

    # Basic outline; booking systems not yet integrated
    return {
        "date": str(today),
        "tomorrow": str(tomorrow),
        "summary": {
            "recent_handovers": [
                {"date": str(h.date), "outlet": h.outlet, "shift": h.shift, "covers": h.covers}
                for h in handovers
            ],
            "open_incidents": [
                {"id": i.id, "title": i.title, "severity": i.severity, "status": i.status}
                for i in open_incidents
            ],
            "due_actions": [
                {"id": a.id, "title": a.title, "owner": a.owner, "due_date": str(a.due_date) if a.due_date else None}
                for a in due_actions
            ],
            "bookings": {"note": "Integration pending", "items": []},
        },
    }

