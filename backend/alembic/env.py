"""
DocuMind AI — Alembic environment configuration.

Configured for async SQLAlchemy (asyncpg driver).
- Reads DATABASE_URL from the application settings (via .env).
- Loads all ORM models so autogenerate can detect schema changes.
- Uses asyncio run_sync pattern required for async engines.
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# ---- Alembic config object ----
config = context.config

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---- Import application models and settings ----
# Must happen BEFORE target_metadata is set so all models are registered.
from app.core.config import settings  # noqa: E402
from app.database.base import Base  # noqa: E402
from app.database import models  # noqa: E402, F401  ← registers all ORM models

target_metadata = Base.metadata

# Override sqlalchemy.url from our application settings (not from alembic.ini).
# This means DATABASE_URL in .env is the single source of truth.
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode (generates SQL without a live connection).
    Useful for reviewing SQL before applying.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,        # detect column type changes
        compare_server_default=True,  # detect server default changes
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode using an async engine.
    Uses NullPool so Alembic connections are not pooled (safest for migrations).
    """
    connectable = create_async_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
