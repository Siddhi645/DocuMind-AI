"""
DocuMind AI — Database Base
Async SQLAlchemy engine, session factory, and declarative base.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# ---- Engine ----
# Note: create_async_engine() does NOT open a database connection at import time.
# asyncpg only resolves and connects when the first actual query/begin() is called.
# This means the application starts successfully even when PostgreSQL is offline.
# The first real connection attempt occurs in create_tables() during the lifespan
# startup — that call is already wrapped in a try/except in main.py, so startup
# failure is non-fatal in development.
# In production: use Alembic migrations instead of create_tables().
engine = create_async_engine(
    settings.database_url,
    echo=settings.is_development,  # Log SQL in development only
    pool_pre_ping=True,            # Detect stale connections before use
    pool_size=5,
    max_overflow=10,
)

# ---- Session factory ----
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ---- Declarative Base ----
class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# ---- Dependency ----
async def get_db() -> AsyncSession:
    """
    FastAPI dependency that provides an async database session.

    Usage in endpoints:
        async def my_endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables() -> None:
    """
    Create all database tables from ORM models.
    Called once at application startup (development only).
    In production, use Alembic migrations instead.
    """
    # Import models here to ensure they're registered with Base
    from app.database import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created (or already exist).")
