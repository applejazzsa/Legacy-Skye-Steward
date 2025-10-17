from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from . import models  # <-- important: ensures tables are known

from .api.analytics import router as analytics_router
from .api.incidents import router as incidents_router
from .api.handovers import router as handovers_router
from .api.handover import router as handover_router
from .api.guest_notes import router as guest_notes_router

app = FastAPI(title="Legacy Steward API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(analytics_router)
app.include_router(incidents_router)
app.include_router(handovers_router)
app.include_router(handover_router)
app.include_router(guest_notes_router)
