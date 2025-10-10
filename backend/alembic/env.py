# C:\Dev\LegacySkyeSteward\backend\alembic\env.py

from __future__ import annotations

from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool

# Import your project's Base and DATABASE_URL
from app.db import Base, DATABASE_URL

# This Alembic Config object provides access to the .ini values in alembic.ini.
config = context.config

# If you want alembic.ini’s sqlalchemy.url to be ignored, we’ll push DATABASE_URL in code.
# Ensure logging configuration is loaded if present
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Tell Alembic which metadata to autogenerate against
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # also detect column type changes
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Build a minimal config dict that injects our DATABASE_URL
    ini_section = config.get_section(config.config_ini_section) or {}
    ini_section["sqlalchemy.url"] = DATABASE_URL

    connectable = engine_from_config(
        ini_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
