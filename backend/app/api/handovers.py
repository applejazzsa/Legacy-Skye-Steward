from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Handover

router = APIRouter(prefix="/api/handovers", tags=["handovers"])

@router.get("/recent")
def recent_handovers(db: Session = Depends(get_db)):
    items = db.query(Handover).order_by(Handover.date.desc(), Handover.id.desc()).limit(10).all()
    return {
        "items": [
            {"id": h.id, "date": h.date.isoformat(), "outlet": h.outlet, "shift": h.shift, "covers": h.covers}
            for h in items
        ]
    }
