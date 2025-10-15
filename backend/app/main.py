from __future__ import annotations

from typing import List
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app import crud, schemas
from app.analytics import get_top_items, get_kpi_summary

app = FastAPI(title="Steward API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# safety net so local dev works even without migrations
@app.on_event("startup")
def _startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/api/handover", response_model=List[schemas.HandoverRead])
def list_handovers(db: Session = Depends(get_db)):
    return crud.list_handovers(db)

@app.get("/api/guest-notes", response_model=List[schemas.GuestNoteOut])
def list_guest_notes(db: Session = Depends(get_db)):
    return crud.list_guest_notes(db)

@app.get("/api/analytics/top-items")
def analytics_top_items(limit: int = 5, db: Session = Depends(get_db)):
    return {"items": get_top_items(db, limit=limit)}

@app.get("/api/analytics/kpi-summary")
def analytics_kpi_summary(target: float = 10000, db: Session = Depends(get_db)):
    return get_kpi_summary(db, target=target)
