"""
Shared test fixtures.
"""

import os
import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Set test environment variables before importing app modules
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///test.db")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-token")
os.environ.setdefault("WEBAPP_URL", "http://localhost:3000")
os.environ.setdefault("ADMIN_DASHBOARD_URL", "http://localhost:3001")
os.environ.setdefault("ADMIN_API_KEY", "test-admin-key")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret")
os.environ.setdefault("ENVIRONMENT", "dev")

from app.main import create_app
from app.models import Base  # noqa: F401  — ensures all models are registered
import app.models  # noqa: F401  — import all model modules


# ---------- HTTP client fixture ----------

@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Provide an async HTTP test client."""
    application = create_app()
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------- In-memory SQLite DB for model tests ----------

TEST_DB_URL = "sqlite+aiosqlite://"
test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=False)
async def db_session():
    """Yield a clean DB session with all tables created (in-memory SQLite)."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestSessionLocal() as session:
        yield session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
