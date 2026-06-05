"""Seed script — creates default admin user (idempotent).

Run via: python -m app.seed
Environment variables:
  SEED_ADMIN_EMAIL     (default: admin@test.com)
  SEED_ADMIN_PASSWORD  (default: admin123)
  SEED_ADMIN_FULL_NAME (default: Test Admin)
"""

import asyncio
import os
import sys

from sqlalchemy import select

from app.constants import AdminRole
from app.database import async_session_factory
from app.models.admin import Admin
from app.services.auth_service import AuthService


async def seed_admin() -> None:
    """Create the default admin user if it does not already exist."""
    email = os.environ.get("SEED_ADMIN_EMAIL", "admin@test.com")
    password = os.environ.get("SEED_ADMIN_PASSWORD", "admin123")
    full_name = os.environ.get("SEED_ADMIN_FULL_NAME", "Test Admin")

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