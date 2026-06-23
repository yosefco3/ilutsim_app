"""
AdminService — business logic for admin dashboard management.
"""

import logging

from app.models.admin import Admin
from app.repositories.admin_repository import AdminRepository
from app.schemas.user_schemas import AdminCreate, AdminResponse
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

    async def get_all_admins(self) -> list[AdminResponse]:
        """Return all admins."""
        admins = await self._admin_repo.get_all()
        return [AdminResponse.model_validate(a) for a in admins]
