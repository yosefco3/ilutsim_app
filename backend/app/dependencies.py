"""
Dependency injection for FastAPI routes.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for route handlers."""
    async for session in get_db_session():
        yield session


async def get_current_user() -> None:
    """Placeholder — will be implemented in Step 5 (Controllers)."""
    return None