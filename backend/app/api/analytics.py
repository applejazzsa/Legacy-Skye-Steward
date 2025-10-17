from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Handover, Incident, SaleItem

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/kpi-summary")
def kpi_summary(target: Optional[int] = None, db: Session = Depends(get_db)):
    since = date.today() - timedelta(days=7)

    total_covers = db.query(func.coalesce(func.sum(Handover.covers), 0))\
                     .filter(Handover.date >= since).scalar()

    # revenue_7d placeholder – using qty as "amount" for now (extend with prices later)
    revenue_7d = db.query(func.coalesce(func.sum(SaleItem.qty * 1000), 0))\
                   .filter(SaleItem.sold_on >= since).scalar()  # pretend each qty ~ 1000 units

    incidents_open = db.query(Incident).filter(Incident.status.in_(["OPEN", "IN_PROGRESS"])).count()

    top_row = db.query(SaleItem.name, func.sum(SaleItem.qty).label("q"))\
                .filter(SaleItem.sold_on >= since)\
                .group_by(SaleItem.name)\
                .order_by(func.sum(SaleItem.qty).desc())\
                .first()
    top_name = top_row[0] if top_row else None
    top_qty = int(top_row[1]) if top_row else 0

    return {
        # snake_case
        "total_covers_7d": int(total_covers or 0),
        "revenue_7d": int(revenue_7d or 0),
        "incidents_open": int(incidents_open or 0),
        "top_seller": {"item": top_name, "name": top_name, "qty": top_qty},
        # camelCase mirrors
        "totalCovers7d": int(total_covers or 0),
        "revenue7d": int(revenue_7d or 0),
        "incidentsOpen": int(incidents_open or 0),
        "topSeller": {"item": top_name, "name": top_name, "qty": top_qty},
        "target": target,
    }

@router.get("/top-items")
def top_items(limit: int = 5, db: Session = Depends(get_db)):
    since = date.today() - timedelta(days=7)
    rows = db.query(SaleItem.name, func.sum(SaleItem.qty).label("q"))\
             .filter(SaleItem.sold_on >= since)\
             .group_by(SaleItem.name)\
             .order_by(func.sum(SaleItem.qty).desc())\
             .limit(limit).all()
    return {"items": [{"name": r[0], "qty": int(r[1])} for r in rows]}
