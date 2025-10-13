"""Database configuration utilities."""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .config import get_database_url


class Base(DeclarativeBase):
    """Declarative base class for SQLAlchemy models."""


_DATABASE_URL = get_database_url()
_SQLITE_PREFIX = "sqlite"

_engine_kwargs: dict[str, object] = {}
_connect_args: dict[str, object] = {}

if _DATABASE_URL.startswith(_SQLITE_PREFIX):
    _connect_args["check_same_thread"] = False
    if _DATABASE_URL == "sqlite:///:memory:":
        _engine_kwargs["poolclass"] = StaticPool

engine = create_engine(
    _DATABASE_URL,
    connect_args=_connect_args,
    future=True,
    **_engine_kwargs,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_session() -> Session:
    """Return a new SQLAlchemy session."""

    return SessionLocal()


__all__ = ["Base", "engine", "SessionLocal", "get_session"]
