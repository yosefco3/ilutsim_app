"""
Async database engine and session factory.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

settings = get_settings()

_engine_kwargs: dict = {
    "echo": settings.ENVIRONMENT == "dev",
}
# pool_size / max_overflow are not valid for SQLite (tests)
if settings.DATABASE_URL.startswith("postgresql"):
    _engine_kwargs["pool_size"] = 5
    _engine_kwargs["max_overflow"] = 10

async_engine = create_async_engine(
    settings.DATABASE_URL,
    **_engine_kwargs,
)

async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_pool() -> AsyncSession:  # type: ignore[misc]
    """Yield an async database session (alias used by dependency injection)."""
    async with async_session_factory() as session:
        yield session


# Keep backward-compatible alias
get_db_session = get_pool
