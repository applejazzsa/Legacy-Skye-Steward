from __future__ import annotations

# Compatibility shim so all routes import the DB dependency from here.
# New code should import only `get_db` from app.deps.

from .db import get_db  # re-export for routes

# Legacy alias for older code that still imports `get_session` from app.deps/app.db
def get_session():
    # Yielding the same generator keeps type/behavior compatible.
    return get_db()
