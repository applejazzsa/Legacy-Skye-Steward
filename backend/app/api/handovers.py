from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Handover
from ..tenant import get_tenant

router = APIRouter(prefix="/api/handovers", tags=["handovers"])

@router.get("/recent")
def recent_handovers(db: Session = Depends(get_db), tenant: str = Depends(get_tenant)):
    items = (db.query(Handover)
             .filter(Handover.tenant_id == tenant)
             .order_by(Handover.date.desc(), Handover.id.desc())
             .limit(10).all())
    return {
        "items": [
            {"id": h.id, "date": h.date.isoformat(), "outlet": h.outlet, "shift": h.shift, "covers": h.covers}
            for h in items
        ]
    }
