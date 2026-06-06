"""
Scheduled tasks: closing reminders and week auto-close.
Uses APScheduler for cron-like scheduling.
"""

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings

logger = logging.getLogger("ilutzim")

scheduler = AsyncIOScheduler(timezone="Asia/Jerusalem")


async def _send_closing_reminders():
    """Send reminders to users who haven't submitted for the active week."""
    try:
        from app.services.user_service import UserService
        from app.services.week_service import WeekService
        from app.services.submission_service import SubmissionService
        from app.repositories.user_repository import UserRepository
        from app.database import get_session
        from app.bot.notifications import notify_closing_reminder

        async with get_session() as session:
            user_svc = UserService(UserRepository(session))
            week_svc = WeekService(session)
            sub_svc = SubmissionService(session)

            week = await week_svc.get_active_week()
            if week is None:
                return

            # Get all active users
            users = await user_svc.get_all_active_users()
            if not users:
                return

            # Find users who haven't submitted
            non_submitters = []
            for user in users:
                submission = await sub_svc.get_user_submission(user["id"], week["id"])
                if submission is None:
                    tg_id = user.get("telegram_id")
                    if tg_id:
                        non_submitters.append(tg_id)

        if non_submitters:
            deadline = week.get("submission_deadline", "")
            await notify_closing_reminder(
                week_start=week["week_start_date"],
                deadline_text=str(deadline) if deadline else "בקרוב",
                telegram_ids=non_submitters,
            )
            logger.info("Closing reminders sent to %d users", len(non_submitters))

    except Exception as exc:
        logger.error("Error in closing reminder cron: %s", exc)


def setup_cron_jobs():
    """Register all scheduled jobs."""
    # Closing reminder at configured hour (default 18:00 IL time)
    reminder_hour = settings.reminder_hour
    scheduler.add_job(
        _send_closing_reminders,
        "cron",
        hour=reminder_hour,
        minute=0,
        id="closing_reminder",
        replace_existing=True,
    )
    logger.info("Scheduled closing reminder job at hour=%d", reminder_hour)