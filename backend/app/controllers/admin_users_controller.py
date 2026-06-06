"""
AdminUsersController — admin endpoints for user management.
"""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.dependencies import get_user_service, require_admin_role
from app.schemas.user_schemas import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

logger = logging.getLogger("ilutzim")

router = APIRouter(
    prefix="/admin/users",
    tags=["Admin – Users"],
    dependencies=[Depends(require_admin_role)],
)

DUPLICATE_PHONE_MSG = "מספר טלפון זה כבר קיים במערכת"


def _is_duplicate_phone_error(exc: IntegrityError) -> bool:
    """Check whether the IntegrityError is a duplicate phone_number violation.

    Works across all asyncpg versions and SQLAlchemy exception wrapping
    by inspecting the string representation of the error.
    """
    err_str = str(exc).lower()
    return "uniqueviolation" in err_str or (
        "duplicate key" in err_str and "phone_number" in err_str
    )


@router.get("", response_model=list[UserResponse])
async def list_users(
    user_service: UserService = Depends(get_user_service),
):
    """List all users (active and inactive) for admin management."""
    return await user_service.get_all_users()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    user_service: UserService = Depends(get_user_service),
):
    """Create a new guard user."""
    try:
        user = await user_service.create_user(data)
        return user
    except IntegrityError as e:
        logger.warning(f"User creation integrity error: {e}")
        if _is_duplicate_phone_error(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=DUPLICATE_PHONE_MSG,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="שגיאה ביצירת המשתמש",
        )
    except Exception as e:
        logger.error(f"User creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


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
    except IntegrityError as e:
        logger.warning(f"User update integrity error: {e}")
        if _is_duplicate_phone_error(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=DUPLICATE_PHONE_MSG,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="שגיאה בעדכון המשתמש",
        )
    except Exception as e:
        logger.error(f"User update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: uuid.UUID,
    user_service: UserService = Depends(get_user_service),
):
    """Permanently delete a user from the database."""
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
