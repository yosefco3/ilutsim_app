"""
AdminWeeksController — admin endpoints for schedule week management.
"""

import logging
import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.constants import WeekStatus
from app.dependencies import get_week_service, require_admin_role
from app.exceptions import AppBaseException
from app.schemas.week_schemas import WeekCreate, WeekResponse, WeekStatusUpdate
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


@router.post("/open", response_model=WeekResponse, status_code=status.HTTP_201_CREATED)
async def open_week(
    start_date: Optional[date] = Query(
        None, description="Sunday for the new week (default: upcoming Sunday)"
    ),
    week_service: WeekService = Depends(get_week_service),
):
    """Open the next schedule week. Refuses 409 if a week is already open."""
    try:
        return await week_service.open_new_week(start_date)
    except AppBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.get("/{week_id}", response_model=WeekResponse)
async def get_week(
    week_id: uuid.UUID,
    week_service: WeekService = Depends(get_week_service),
):
    """Get a specific week by ID."""
    try:
        return await week_service.get_week(week_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Week not found",
        )


@router.post("/{week_id}/open", response_model=WeekResponse)
async def reopen_week(
    week_id: uuid.UUID,
    week_service: WeekService = Depends(get_week_service),
):
    """Re-open a closed or locked week for submissions."""
    try:
        return await week_service.change_week_status(week_id, WeekStatus.OPEN)
    except AppBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    except Exception as e:
        logger.error(f"Week reopen failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch("/{week_id}/status", response_model=WeekResponse)
async def update_week_status(
    week_id: uuid.UUID,
    body: WeekStatusUpdate,
    week_service: WeekService = Depends(get_week_service),
):
    """Change a week's status (open → locked → published)."""
    try:
        return await week_service.change_week_status(week_id, body.status)
    except Exception as e:
        logger.error(f"Week status change failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
