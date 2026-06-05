"""Seed script — creates default admin user (idempotent).

Run via: python -m app.seed
All seed values come from config.py (which reads .env).
Override via .env: SEED_ADMIN_EMAIL, SEED_ADMIN_PASSWORD, SEED_ADMIN_FULL_NAME
"""

import asyncio

from sqlalchemy import select

from app.config import settings
from app.constants import AdminRole
from app.database import async_session_factory
from app.models.admin import Admin
from app.services.auth_service import AuthService


async def seed_admin() -> None:
    """Create the default admin user if it does not already exist."""
    email = settings.SEED_ADMIN_EMAIL
    password = settings.SEED_ADMIN_PASSWORD
    full_name = settings.SEED_ADMIN_FULL_NAME

    async with async_session_factory() as session:
        result = await session.execute(
            select(Admin).where(Admin.email == email)
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"  Admin user '{email}' already exists (id={existing.id}). Skipping.")
            return

        admin = Admin(
            email=email,
            password_hash=AuthService.hash_password(password),
            full_name=full_name,
            role=AdminRole.SUPER_ADMIN,
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        print(f"  Created admin user '{email}' (id={admin.id}).")


if __name__ == "__main__":
    asyncio.run(seed_admin())