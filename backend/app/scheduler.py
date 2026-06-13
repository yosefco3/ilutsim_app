"""Background scheduler — the automatic Saturday-night (Motzaei Shabbat) rollover.

Every Sunday at 00:00 (Israel time) the active submission week is auto-locked and
the upcoming week is ensured, regardless of admin action. The actual logic lives
in ``WeekService.auto_advance_weeks`` and is idempotent/self-healing, so this
module only owns the *timing*: a weekly cron trigger plus a one-shot catch-up on
startup (covering a server that was down at midnight).
"""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import get_settings

logger = logging.getLogger("ilutzim")

_ROLLOVER_JOB_ID = "weekly_week_rollover"


async def run_weekly_rollover() -> None:
    """Lock the expired open week and ensure the upcoming one.

    Uses its own committed session (``get_session``) since it runs outside the
    FastAPI request lifecycle. Failures are logged and swallowed — the next run
    (or any admin weeks-list load) self-heals because the logic is idempotent.
    """
    try:
        from app.database import get_session
        from app.repositories.schedule_week_repository import ScheduleWeekRepository
        from app.repositories.user_repository import UserRepository
        from app.services.week_service import WeekService

        async with get_session() as session:
            week_repo = ScheduleWeekRepository(session)
            user_repo = UserRepository(session)
            service = WeekService(week_repo, user_repo)
            await service.auto_advance_weeks()
        logger.info("Weekly rollover completed")
    except Exception as exc:
        logger.warning("Weekly rollover failed: %s", exc)


def start_scheduler() -> AsyncIOScheduler | None:
    """Start the weekly rollover scheduler. Returns the scheduler, or None if
    disabled. Must be called inside a running event loop (FastAPI lifespan)."""
    settings = get_settings()
    if not settings.AUTO_ROLLOVER_ENABLED:
        logger.info("Auto rollover disabled (AUTO_ROLLOVER_ENABLED=false)")
        return None

    scheduler = AsyncIOScheduler(timezone=settings.SCHEDULER_TIMEZONE)
    # Motzaei Shabbat 00:00 == Sunday 00:00 Israel time.
    scheduler.add_job(
        run_weekly_rollover,
        trigger="cron",
        day_of_week="sun",
        hour=0,
        minute=0,
        id=_ROLLOVER_JOB_ID,
        replace_existing=True,
        misfire_grace_time=3600,
        coalesce=True,
    )
    scheduler.start()
    logger.info(
        "Weekly rollover scheduled: Sun 00:00 %s", settings.SCHEDULER_TIMEZONE
    )
    return scheduler
