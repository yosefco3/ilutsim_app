"""
AdminUsersController — admin endpoints for user management.
"""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_user_service, require_admin_role
from app.schemas.user_schemas import UserResponse, UserUpdate
from app.services.user_service import UserService

logger = logging.getLogger("ilutzim")

router = APIRouter(
    prefix="/admin/users",
    tags=["Admin – Users"],
    dependencies=[Depends(require_admin_role)],
)


@router.get("", response_model=list[UserResponse])
async def list_users(
    user_service: UserService = Depends(get_user_service),
):
    """List all active users."""
    return await user_service.get_active_users()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    user_service: UserService = Depends(get_user_service),
):
    """Get a single user by ID."""
    user = await user_service.get_user(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
):
    """Update user details."""
    try:
        user = await user_service.update_user(user_id, data)
        return user
    except Exception as e:
        logger.error(f"User update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: uuid.UUID,
    user_service: UserService = Depends(get_user_service),
):
    """Soft-delete (deactivate) a user."""
    success = await user_service.deactivate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )