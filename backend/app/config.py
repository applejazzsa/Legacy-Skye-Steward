from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env in backend/
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

def get_database_url() -> str:
    """
    Use absolute SQLite path by default so Alembic and the app point to the same file.
    Env var DATABASE_URL can override (e.g., sqlite:///C:/path/to/steward.db).
    """
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    # Default SQLite file inside backend/ as an absolute path
    db_path = (BASE_DIR / "steward.db").resolve()
    # On Windows absolute sqlite URL must be sqlite:///C:/full/path.db
    return f"sqlite:///{db_path.as_posix()}"
