"""
AdminAdminsController — admin endpoints for managing admin accounts.
"""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_admin_service, require_admin_role
from app.services.admin_service import AdminService

logger = logging.getLogger("ilutzim")

router = APIRouter(
    prefix="/admin/admins",
    tags=["Admin – Admins"],
    dependencies=[Depends(require_admin_role)],
)


@router.get("")
async def list_admins(
    admin_service: AdminService = Depends(get_admin_service),
):
    """List all admin accounts."""
    return await admin_service.get_all_admins()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_admin(
    telegram_id: int,
    display_name: str,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Create a new admin account."""
    try:
        return await admin_service.create_admin(telegram_id, display_name)
    except Exception as e:
        logger.error(f"Admin creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_admin(
    admin_id: uuid.UUID,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Remove an admin account."""
    success = await admin_service.remove_admin(admin_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found",
        )