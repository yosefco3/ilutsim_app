"""
AdminWeeksController — admin endpoints for schedule week management.
"""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.constants import WeekStatus
from app.dependencies import get_week_service, require_admin_role
from app.schemas.week_schemas import WeekCreate, WeekResponse
from app.services.week_service import WeekService

logger = logging.getLogger("ilutzim")

router = APIRouter(
    prefix="/admin/weeks",
    tags=["Admin – Weeks"],
    dependencies=[Depends(require_admin_role)],
)


@router.get("", response_model=list[WeekResponse])
async def list_weeks(
    week_service: WeekService = Depends(get_week_service),
):
    """List all schedule weeks."""
    return await week_service.get_all_weeks()


@router.post("", response_model=WeekResponse, status_code=status.HTTP_201_CREATED)
async def create_week(
    data: WeekCreate,
    week_service: WeekService = Depends(get_week_service),
):
    """Create a new schedule week."""
    try:
        return await week_service.create_week(data)
    except Exception as e:
        logger.error(f"Week creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{week_id}", response_model=WeekResponse)
async def get_week(
    week_id: uuid.UUID,
    week_service: WeekService = Depends(get_week_service),
):
    """Get a specific week by ID."""
    try:
        return await week_service.change_week_status(week_id, WeekStatus.OPEN)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Week not found",
        )


@router.patch("/{week_id}/status", response_model=WeekResponse)
async def update_week_status(
    week_id: uuid.UUID,
    new_status: WeekStatus,
    week_service: WeekService = Depends(get_week_service),
):
    """Change a week's status (open → locked → published)."""
    try:
        return await week_service.change_week_status(week_id, new_status)
    except Exception as e:
        logger.error(f"Week status change failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )