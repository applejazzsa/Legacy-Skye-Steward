import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1) DATABASE_URL from env, fallback to local sqlite file in project root
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./steward.db").strip()

# 2) SQLite requires a special connect arg for multithreading; others don't
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

# 3) Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4) Base class for ORM models
Base = declarative_base()

# 5) Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
