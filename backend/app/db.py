# C:\Dev\LegacySkyeSteward\backend\app\db.py

from __future__ import annotations

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Expose a DATABASE_URL that Alembic and the app can both use
# Default to a local SQLite DB file next to your backend code.
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# For SQLite we need the check_same_thread flag; for others (e.g. Postgres) we don't.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)

Base = declarative_base()


# FastAPI dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
