from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import RevenueEntry
from ..deps import get_active_tenant, require_role

router = APIRouter(prefix="/api/finance", tags=["finance"])


@router.post("/revenue", dependencies=[Depends(require_role("manager"))])
def add_revenue_entry(payload: Dict[str, Any], db: Session = Depends(get_db), tenant=Depends(get_active_tenant)):
    """
    Quick-add a tenant-scoped revenue entry. Used for Conference or other misc revenue.
    Body: { category: string, amount: number, occurred_at?: ISO, description?: string }
    Amount is in ZAR; stored as cents (integer) to avoid float rounding.
    """
    try:
        amount = float(payload.get("amount") or 0.0)
    except Exception:
        raise HTTPException(status_code=400, detail="invalid amount")
    category = (payload.get("category") or "").strip() or "Other"
    when = payload.get("occurred_at")
    try:
        when_dt = datetime.fromisoformat(when.replace("Z", "+00:00")) if when else datetime.utcnow()
    except Exception:
        when_dt = datetime.utcnow()

    entry = RevenueEntry(
        tenant_id=str(getattr(tenant, 'slug', '') or getattr(tenant, 'id')),
        outlet=(payload.get("outlet") or "Conference"),
        category=category,
        amount_cents=int(round(amount * 100)),
        occurred_at=when_dt,
        description=payload.get("description"),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"id": entry.id}

