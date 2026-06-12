"""
SubmissionController — guard submission endpoints.
"""

import logging
import uuid
from datetime import date, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_current_user, get_settings_service, get_submission_service, get_week_service
from app.messages import Messages
from app.models.user import User
from app.schemas.submission_schemas import (
    GuardSubmissionRequest,
    ShiftWindowInput,
    DayStatusInput,
    SubmissionCreate,
    SubmissionResponse,
)
from app.schemas.week_schemas import WeekWithDaysResponse
from app.services.settings_service import SettingsService
from app.services.submission_service import SubmissionService
from app.services.week_service import WeekService

logger = logging.getLogger("ilutzim")

router = APIRouter(prefix="/submissions", tags=["Submissions"])


@router.get("/current-week", response_model=WeekWithDaysResponse | None)
async def get_current_open_week(
    week_service: WeekService = Depends(get_week_service),
):
    """Get the week guards should see for the submission form.

    Returns the open week when one exists; otherwise the latest relevant week
    (closed/locked/published) **with its status**, so the UI can show a status
    banner instead of a generic "no week" error. Returns ``null`` only when no
    week exists at all. Submitting is still gated on the week being OPEN in the
    POST handler below.
    """
    return await week_service.get_relevant_week_with_days()


@router.get("/my", response_model=SubmissionResponse | None)
async def get_my_submission(
    week_id: uuid.UUID = Query(..., description="Week ID"),
    current_user: User = Depends(get_current_user),
    submission_service: SubmissionService = Depends(get_submission_service),
):
    """Get the authenticated guard's submission for a given week.

    Returns ``null`` if no submission exists yet.
    """
    return await submission_service.get_submission(current_user.id, week_id)


@router.post("", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def submit_schedule(
    data: GuardSubmissionRequest,
    current_user: User = Depends(get_current_user),
    submission_service: SubmissionService = Depends(get_submission_service),
    week_service: WeekService = Depends(get_week_service),
):
    """Submit a guard's weekly schedule preferences.

    The week must be open for submissions.
    The guard is authenticated via Telegram WebApp init data.
    """
    # Guard: must have an open week
    open_week = await week_service.get_current_open_week()
    if open_week is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=Messages.SUBMISSION_CLOSED,
        )
    if str(open_week.id) != str(data.week_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=Messages.SUBMISSION_WRONG_WEEK,
        )

    # Convert GuardSubmissionRequest → SubmissionCreate
    try:
        submission_create = _convert_guard_request(data, open_week.start_date, current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    try:
        submission = await submission_service.create_submission(submission_create)
    except Exception as e:
        logger.error(f"Submission failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Send Telegram success notification (non-critical — failure is logged but not returned)
    if current_user.telegram_id:
        try:
            from app.bot.notifications import notify_submission_success
            week_label = f"{open_week.start_date.strftime('%d/%m/%Y')} - {open_week.end_date.strftime('%d/%m/%Y')}"
            await notify_submission_success(int(current_user.telegram_id), week_label)
        except Exception as e:
            logger.warning(f"Failed to send submission success notification: {e}")

    return submission


@router.get("/shift-defaults")
async def get_shift_defaults(
    settings_service: SettingsService = Depends(get_settings_service),
):
    """Return the default shift hours (editable by admin via /admin/settings).

    Used by the guard submission form to pre-fill hours when a shift is toggled on.
    Public endpoint — no auth required.
    """
    keys = ("shift_default_morning", "shift_default_afternoon", "shift_default_night")
    result = {}
    for key in keys:
        raw = await settings_service.get_setting(key)
        parts = (raw or "").split("-")
        result[key] = {
            "from_hour": parts[0] if len(parts) >= 1 else "",
            "to_hour": parts[1] if len(parts) >= 2 else "",
        }
    return result


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


# ── Helpers ──────────────────────────────────────────────────────────────────

def _parse_time(hour_str: str | None) -> time:
    """Parse 'HH:MM' or 'HH:MM:SS' into a time object.  Defaults to 00:00."""
    if not hour_str or not hour_str.strip():
        return time(0, 0)
    parts = hour_str.strip().split(":")
    h, m = int(parts[0]) % 24, int(parts[1]) % 60 if len(parts) > 1 else 0
    return time(h, m)


def _convert_guard_request(
    data: GuardSubmissionRequest,
    week_start: date,
    user_id: uuid.UUID,
) -> SubmissionCreate:
    """Convert a GuardSubmissionRequest to SubmissionCreate for the service layer."""
    days: list[DayStatusInput] = []
    for d in data.days:
        day_date = week_start + timedelta(days=d.day_index)
        shifts: list[ShiftWindowInput] = []
        for s in d.shifts:
            # Skip shifts with empty from_hour or to_hour (guard didn't fill hours)
            if not s.from_hour or not s.from_hour.strip():
                continue
            if not s.to_hour or not s.to_hour.strip():
                continue
            shifts.append(
                ShiftWindowInput(
                    shift_type=s.shift_type,
                    start_time=_parse_time(s.from_hour),
                    end_time=_parse_time(s.to_hour),
                )
            )
        day_status = DayStatusInput(
            date=day_date,
            is_available=len(shifts) > 0,
            shifts=shifts,
        )
        days.append(day_status)

    return SubmissionCreate(
        week_id=data.week_id,
        user_id=user_id,
        general_notes=data.general_notes,
        days=days,
    )
