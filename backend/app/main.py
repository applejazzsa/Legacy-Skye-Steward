# app/main.py
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.deps import get_db
from app import models, crud, schemas
from app.db import engine, Base
from app.analytics import top_items, staff_praise, kpi_summary

# create tables (dev)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Legacy Skye Steward API",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "service": "Legacy Skye Steward API"}

@app.get("/health")
def health():
    return {"status": "healthy", "time": datetime.utcnow().isoformat()}

# ---- Handover CRUD ----

@app.post("/api/handover", response_model=schemas.HandoverRead)
def create_handover(payload: schemas.HandoverCreate, db: Session = Depends(get_db)):
    return crud.create_handover(db, payload)

@app.get("/api/handover/{handover_id}", response_model=schemas.HandoverRead)
def read_handover(handover_id: int, db: Session = Depends(get_db)):
    item = crud.get_handover(db, handover_id)
    if not item:
        raise HTTPException(status_code=404, detail="Handover not found")
    return item

@app.get("/api/handover", response_model=List[schemas.HandoverRead])
def list_handovers(
    outlet: Optional[str] = None,
    start_date: Optional[str] = Query(None, description="ISO date e.g. 2025-09-01"),
    end_date: Optional[str] = Query(None, description="ISO date e.g. 2025-09-30"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return crud.list_handovers(db, outlet=outlet, start_date=start_date, end_date=end_date, skip=skip, limit=limit)

@app.put("/api/handover/{handover_id}", response_model=schemas.HandoverRead)
def update_handover(handover_id: int, payload: schemas.HandoverUpdate, db: Session = Depends(get_db)):
    updated = crud.update_handover(db, handover_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Handover not found")
    return updated

@app.delete("/api/handover/{handover_id}")
def delete_handover(handover_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_handover(db, handover_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Handover not found")
    return {"deleted": True, "id": handover_id}

# ---- Analytics (uses app.deps.get_db) ----

@app.get("/api/analytics/top-items")
def analytics_top_items(
    start_date: str | None = Query(None, description="ISO date/time"),
    end_date: str | None = Query(None, description="ISO date/time"),
    limit: int = Query(5, ge=1, le=50),
    outlet: str | None = None,
    db: Session = Depends(get_db),
):
    return top_items(db, start_date, end_date, limit=limit, outlet=outlet)

@app.get("/api/analytics/staff-praise")
def analytics_staff_praise(
    start_date: str | None = Query(None, description="ISO date/time"),
    end_date: str | None = Query(None, description="ISO date/time"),
    limit: int = Query(5, ge=1, le=50),
    outlet: str | None = None,
    db: Session = Depends(get_db),
):
    return staff_praise(db, start_date, end_date, limit=limit, outlet=outlet)

@app.get("/api/analytics/kpi-summary")
def analytics_kpi_summary(
    target: str | None = Query(None, description="Optional total revenue target as number string"),
    outlet: str | None = None,
    db: Session = Depends(get_db),
):
    return kpi_summary(db, target=target, outlet=outlet)
