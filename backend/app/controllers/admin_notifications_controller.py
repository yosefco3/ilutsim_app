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
    # Raises a not-found exception if the week doesn't exist.
    week = await week_service.get_week(week_id)

    users = await user_service.get_all_active_users()

    # Collect active guards who haven't submitted yet, keeping their name so the
    # reminder can greet each one personally.
    recipients: list[dict] = []
    for user in users:
        submission = await submission_service.get_submission(user.id, week_id)
        if submission is None and user.telegram_id:
            try:
                telegram_id = int(user.telegram_id)
            except (TypeError, ValueError):
                logger.warning("Skipping invalid telegram_id for user %s", user.id)
                continue
            name = (getattr(user, "full_name", None)
                    or f"{user.first_name} {user.last_name}").strip()
            recipients.append({"telegram_id": telegram_id, "name": name})

    # Send via bot
    sent_count = 0
    if recipients:
        try:
            from app.bot.notifications import notify_closing_reminder

            sent_count = await notify_closing_reminder(
                week_start=week.start_date,
                week_end=getattr(week, "end_date", None),
                deadline_text="בקרוב",
                recipients=recipients,
            )
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
    # Raises a not-found exception if the week doesn't exist.
    await week_service.get_week(week_id)

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
