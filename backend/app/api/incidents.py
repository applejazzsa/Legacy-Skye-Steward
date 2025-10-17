from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Incident

router = APIRouter(prefix="/api", tags=["incidents"])

@router.get("/incidents")
def list_incidents(db: Session = Depends(get_db)):
    items = db.query(Incident).filter(Incident.status.in_(["OPEN", "IN_PROGRESS"]))\
              .order_by(Incident.id.desc()).all()
    return {
        "total": len(items),
        "items": [
            {
                "id": i.id, "outlet": i.outlet, "severity": i.severity,
                "title": i.title, "status": i.status
            } for i in items
        ]
    }
