"""Application configuration helpers."""
from __future__ import annotations

from functools import lru_cache
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

# Load environment variables from a .env file if present.
load_dotenv()


class Settings(BaseModel):
    """Settings sourced from environment variables."""

    database_url: str = Field(default="sqlite:///./app.db", alias="DATABASE_URL")
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        alias="CORS_ORIGINS",
    )

    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | List[str]) -> List[str]:
        if isinstance(value, str):
            if not value.strip():
                return []
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()


def get_database_url() -> str:
    """Expose the configured database URL."""

    return get_settings().database_url


def get_cors_origins() -> List[str]:
    """Expose configured CORS origins."""

    origins = get_settings().cors_origins
    return origins if origins else ["http://localhost:3000", "http://127.0.0.1:3000"]


__all__ = ["Settings", "get_settings", "get_database_url", "get_cors_origins"]
