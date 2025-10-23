from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from ..db import get_db
from ..models import Handover, SaleItem
from ..tenant import require_tenant  # returns the string tenant_id

router = APIRouter()

@router.get("/kpi-summary")
def kpi_summary(
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    target: float = Query(10_000.0),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(require_tenant),
):
    q = db.query(SaleItem).filter(SaleItem.tenant_id == tenant_id)
    if date_from:
        q = q.filter(SaleItem.sold_on >= date_from)
    if date_to:
        q = q.filter(SaleItem.sold_on <= date_to)
    rows = q.all()
    food = sum(r.qty for r in rows if (r.category or "").lower() == "food")
    bev  = sum(r.qty for r in rows if (r.category or "").lower() == "beverage")
    total = food + bev
    progress = (total / target) if target else 0.0
    return {"target": float(target), "total": float(total), "food": float(food), "beverage": float(bev), "progress": progress}

@router.get("/revenue-trend")
def revenue_trend(
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(require_tenant),
):
    # Aggregate by day from SaleItem qty as "revenue-ish" (demo)
    from sqlalchemy import func, cast, Date
    q = (
        db.query(cast(SaleItem.sold_on, Date).label("d"), func.sum(SaleItem.qty).label("total"))
        .filter(SaleItem.tenant_id == tenant_id)
        .group_by("d")
        .order_by("d")
    )
    if date_from:
        q = q.filter(SaleItem.sold_on >= date_from)
    if date_to:
        q = q.filter(SaleItem.sold_on <= date_to)
    return [{"date": str(d), "total": float(t or 0)} for d, t in q.all()]

@router.get("/top-items")
def top_items(
    limit: int = 5,
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(require_tenant),
):
    from sqlalchemy import func
    q = (
        db.query(SaleItem.name, func.sum(SaleItem.qty).label("units"))
        .filter(SaleItem.tenant_id == tenant_id)
        .group_by(SaleItem.name)
        .order_by(func.sum(SaleItem.qty).desc())
        .limit(limit)
    )
    if date_from:
        q = q.filter(SaleItem.sold_on >= date_from)
    if date_to:
        q = q.filter(SaleItem.sold_on <= date_to)
    return [{"name": n, "units_sold": int(u or 0), "revenue": 0.0} for n, u in q.all()]
