"""Dependency helpers for FastAPI routes."""
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from .db import get_session


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and ensure cleanup."""

    session = get_session()
    try:
        yield session
    finally:
        session.close()


__all__ = ["get_db"]
