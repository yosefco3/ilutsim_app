"""
SubmissionController — guard submission endpoints.
"""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_submission_service, get_week_service
from app.exceptions import WeekLockedException
from app.schemas.submission_schemas import SubmissionCreate, SubmissionResponse
from app.schemas.week_schemas import WeekResponse
from app.services.submission_service import SubmissionService
from app.services.week_service import WeekService

logger = logging.getLogger("ilutzim")

router = APIRouter(prefix="/submissions", tags=["Submissions"])


@router.get("/current-week", response_model=WeekResponse)
async def get_current_open_week(
    week_service: WeekService = Depends(get_week_service),
):
    """Get the currently open week for submissions."""
    week = await week_service.get_current_open_week()
    if week is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No open week found",
        )
    return week


@router.post("", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def submit_schedule(
    data: SubmissionCreate,
    submission_service: SubmissionService = Depends(get_submission_service),
    week_service: WeekService = Depends(get_week_service),
):
    """
    Submit a guard's weekly schedule preferences.

    The week must be open for submissions.
    """
    # Validate week is open
    try:
        await week_service.validate_week_is_open(data.week_id)
    except WeekLockedException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Week is locked for submissions",
        )

    try:
        submission = await submission_service.submit(data)
        return submission
    except Exception as e:
        logger.error(f"Submission failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/week/{week_id}", response_model=list[SubmissionResponse])
async def get_submissions_for_week(
    week_id: uuid.UUID,
    submission_service: SubmissionService = Depends(get_submission_service),
):
    """Get all submissions for a specific week."""
    return await submission_service.get_submissions_for_week(week_id)


@router.get("/user/{user_id}", response_model=list[SubmissionResponse])
async def get_submissions_for_user(
    user_id: uuid.UUID,
    submission_service: SubmissionService = Depends(get_submission_service),
):
    """Get all submissions for a specific user."""
    return await submission_service.get_submissions_for_user(user_id)