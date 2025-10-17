from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from .db import Base, engine, get_db

# If you already have models (e.g., from .models import *), import them
# so their metadata is registered before create_all().
# from .models import *  # noqa: F401

app = FastAPI(title="Legacy Steward API", version="0.1.0")

@app.on_event("startup")
def on_startup():
    """Create tables for SQLite dev by default.
    In production with migrations (Alembic), you can disable this.
    """
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    # DB dependency proves Session works; we don't need to query anything here.
    return {"status": "ok"}
