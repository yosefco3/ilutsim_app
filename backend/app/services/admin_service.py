"""
AdminService — business logic for admin dashboard management.
"""

import logging
import uuid
from typing import Optional

from app.constants import AdminRole
from app.exceptions import UserNotFoundException
from app.models.admin import Admin
from app.repositories.admin_repository import AdminRepository
from app.schemas.user_schemas import AdminCreate, AdminResponse, AdminUpdate
from app.services.auth_service import AuthService

logger = logging.getLogger("ilutzim")


class AdminService:
    """Orchestrates admin CRUD and authentication."""

    def __init__(
        self,
        admin_repo: AdminRepository,
        auth_service: AuthService,
    ) -> None:
        self._admin_repo = admin_repo
        self._auth_service = auth_service

    async def create_admin(self, data: AdminCreate) -> AdminResponse:
        """Create a new admin with hashed password."""
        hashed = AuthService.hash_password(data.password)
        admin = Admin(
            email=data.email,
            password_hash=hashed,
            full_name=data.full_name,
            role=data.role,
        )
        created = await self._admin_repo.create(admin)
        logger.info(f"Admin created: {data.email}")
        return AdminResponse.model_validate(created)

    async def update_admin(
        self, admin_id: int, data: AdminUpdate
    ) -> AdminResponse:
        """Update admin details."""
        admin = await self._get_admin_or_raise(admin_id)
        update_data = data.model_dump(exclude_none=True)
        if "password" in update_data:
            update_data["password_hash"] = AuthService.hash_password(
                update_data.pop("password")
            )
        for field, value in update_data.items():
            setattr(admin, field, value)
        updated = await self._admin_repo.update(admin)
        logger.info(f"Admin updated: {admin_id}")
        return AdminResponse.model_validate(updated)

    async def get_all_admins(self) -> list[AdminResponse]:
        """Return all admins."""
        admins = await self._admin_repo.get_all()
        return [AdminResponse.model_validate(a) for a in admins]

    async def get_admin(self, admin_id: int) -> AdminResponse:
        """Get a single admin by ID."""
        admin = await self._get_admin_or_raise(admin_id)
        return AdminResponse.model_validate(admin)

    async def deactivate_admin(self, admin_id: int) -> AdminResponse:
        """Set is_active=False for an admin."""
        admin = await self._get_admin_or_raise(admin_id)
        admin.is_active = False
        updated = await self._admin_repo.update(admin)
        logger.info(f"Admin deactivated: {admin_id}")
        return AdminResponse.model_validate(updated)

    # ── Internal helpers ──────────────────────────────────────────────────

    async def _get_admin_or_raise(self, admin_id: int) -> Admin:
        admin = await self._admin_repo.get_by_id(admin_id)
        if admin is None:
            raise UserNotFoundException()
        return admin