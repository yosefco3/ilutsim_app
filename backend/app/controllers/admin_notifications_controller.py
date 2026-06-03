"""
AdminNotificationsController — admin endpoints for sending notifications.
"""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import (
    get_user_service,
    get_week_service,
    get_submission_service,
    require_admin_role,
)
from app.services.user_service import UserService
from app.services.week_service import WeekService
from app.services.submission_service import SubmissionService

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
    submission_service: SubmissionService = Depends(get_submission_service),
):
    """Send a reminder to guards who haven't submitted yet for a given week."""
    week = await week_service.get_by_id(week_id)
    if week is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Week not found",
        )

    users = await user_service.get_active_users()

    # Collect telegram IDs of users who haven't submitted
    telegram_ids: list[int] = []
    for user in users:
        submission = await submission_service.get_user_submission(user["id"], week_id)
        if submission is None:
            tg_id = user.get("telegram_id")
            if tg_id:
                telegram_ids.append(tg_id)

    # Send via bot
    sent_count = 0
    if telegram_ids:
        try:
            from app.bot.notifications import notify_closing_reminder

            await notify_closing_reminder(
                week_start=week["week_start_date"],
                deadline_text=str(week.get("submission_deadline", "בקרוב")),
                telegram_ids=telegram_ids,
            )
            sent_count = len(telegram_ids)
        except Exception as exc:
            logger.error("Failed to send reminders: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Bot service unavailable",
            ) from exc

    return {
        "message": "Reminder notifications sent",
        "week_id": str(week_id),
        "total_active": len(users),
        "reminded": sent_count,
    }


@router.post("/publish/{week_id}")
async def notify_week_published(
    week_id: uuid.UUID,
    week_service: WeekService = Depends(get_week_service),
):
    """Notify all guards that the schedule for a week has been published."""
    week = await week_service.get_by_id(week_id)
    if week is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Week not found",
        )

    sent_count = 0
    try:
        from app.bot.notifications import notify_week_published as bot_notify

        count = await bot_notify(week_id=week_id)
        sent_count = count or 0
    except Exception as exc:
        logger.error("Failed to send publish notification: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Bot service unavailable",
        ) from exc

    return {
        "message": "Publish notification sent",
        "week_id": str(week_id),
        "notified_count": sent_count,
    }
