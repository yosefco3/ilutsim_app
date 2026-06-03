"""
AdminNotificationsController — admin endpoints for sending notifications.
"""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_user_service, get_week_service, require_admin_role
from app.services.user_service import UserService
from app.services.week_service import WeekService

logger = logging.getLogger("ilutzim")

router = APIRouter(
    prefix="/admin/notifications",
    tags=["Admin – Notifications"],
    dependencies=[Depends(require_admin_role)],
)


@router.post("/remind/{week_id}")
async def send_submission_reminder(
    week_id: uuid.UUID,
    week_service: WeekService = Depends(get_week_service),
    user_service: UserService = Depends(get_user_service),
):
    """
    Send a reminder to guards who haven't submitted yet for a given week.

    Returns the count of guards reminded. Actual sending is handled by the
    Telegram bot service in Step 06.
    """
    week = await week_service.get_by_id(week_id)
    if week is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Week not found",
        )

    # Get users who haven't submitted
    users = await user_service.get_active_users()

    # TODO: In Step 06, integrate with Telegram bot to send actual notifications
    # For now, return a placeholder response
    return {
        "message": "Reminder notification queued",
        "week_id": str(week_id),
        "target_count": len(users),
    }


@router.post("/publish/{week_id}")
async def notify_week_published(
    week_id: uuid.UUID,
    week_service: WeekService = Depends(get_week_service),
):
    """
    Notify all guards that the schedule for a week has been published.

    Actual sending is handled by the Telegram bot service in Step 06.
    """
    week = await week_service.get_by_id(week_id)
    if week is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Week not found",
        )

    # TODO: In Step 06, integrate with Telegram bot to send actual notifications
    return {
        "message": "Publish notification queued",
        "week_id": str(week_id),
    }