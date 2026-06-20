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
_AUTO_OPEN_JOB_ID = "auto_open_week"
_AUTO_LOCK_JOB_ID = "auto_lock_week"

# Process-wide handle to the running scheduler, so the settings endpoint can
# reschedule the automation jobs after the admin edits them (no restart needed).
_scheduler: "AsyncIOScheduler | None" = None


def get_scheduler() -> "AsyncIOScheduler | None":
    """Return the running scheduler instance (None if not started)."""
    return _scheduler


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


async def run_auto_open() -> None:
    """Cron job: open the upcoming closed week (broadcasts to guards).

    Own committed session; idempotency + the silent/broadcast distinction live
    in ``WeekService``. Failures are logged and swallowed.
    """
    try:
        from app.database import get_session
        from app.repositories.schedule_week_repository import ScheduleWeekRepository
        from app.repositories.user_repository import UserRepository
        from app.services.week_service import WeekService

        async with get_session() as session:
            service = WeekService(
                ScheduleWeekRepository(session), UserRepository(session)
            )
            await service.auto_open_relevant_week()
        logger.info("Auto-open job completed")
    except Exception as exc:
        logger.warning("Auto-open job failed: %s", exc)


async def run_auto_lock() -> None:
    """Cron job: silently lock the currently open week. Own committed session."""
    try:
        from app.database import get_session
        from app.repositories.schedule_week_repository import ScheduleWeekRepository
        from app.repositories.user_repository import UserRepository
        from app.services.week_service import WeekService

        async with get_session() as session:
            service = WeekService(
                ScheduleWeekRepository(session), UserRepository(session)
            )
            await service.auto_lock_open_week()
        logger.info("Auto-lock job completed")
    except Exception as exc:
        logger.warning("Auto-lock job failed: %s", exc)


def _apply_automation_job(scheduler, job_id, cfg, func, timezone) -> None:
    """Add/replace the job when enabled, or remove it when disabled."""
    if cfg.get("enabled"):
        scheduler.add_job(
            func,
            trigger="cron",
            day_of_week=cfg["weekday"],
            hour=cfg["hour"],
            minute=cfg["minute"],
            timezone=timezone,
            id=job_id,
            replace_existing=True,
            misfire_grace_time=3600,
            coalesce=True,
        )
        logger.info(
            "Scheduled %s: %s %02d:%02d %s",
            job_id, cfg["weekday"], cfg["hour"], cfg["minute"], timezone,
        )
    elif scheduler.get_job(job_id) is not None:
        scheduler.remove_job(job_id)
        logger.info("Removed disabled automation job: %s", job_id)
    else:
        # enabled=False and no job registered. Log it explicitly so a missing
        # auto-open/auto-lock is visible in the logs (silence here previously
        # made a disabled job indistinguishable from a scheduling failure).
        logger.info("Automation job %s is disabled (enabled=False) — not scheduled", job_id)


async def sync_automation_jobs(scheduler=None) -> None:
    """(Re)build the auto-open/auto-lock cron jobs from the DB settings.

    Reads ``get_auto_open``/``get_auto_lock`` and registers fixed-id jobs
    (``replace_existing=True`` so an edit never duplicates them). A disabled
    block removes its job. Called on startup and after a settings update so a
    change takes effect immediately, without a restart. No-op if the scheduler
    is not running (e.g. AUTO_ROLLOVER_ENABLED=false).
    """
    scheduler = scheduler or _scheduler
    if scheduler is None:
        return

    try:
        from app.database import get_session
        from app.repositories.system_settings_repository import SystemSettingsRepository
        from app.services.settings_service import SettingsService

        async with get_session() as session:
            settings_service = SettingsService(SystemSettingsRepository(session))
            auto_open = await settings_service.get_auto_open()
            auto_lock = await settings_service.get_auto_lock()

        timezone = get_settings().SCHEDULER_TIMEZONE
        _apply_automation_job(scheduler, _AUTO_OPEN_JOB_ID, auto_open, run_auto_open, timezone)
        _apply_automation_job(scheduler, _AUTO_LOCK_JOB_ID, auto_lock, run_auto_lock, timezone)
    except Exception as exc:
        logger.warning("Failed to sync automation jobs: %s", exc)


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

    global _scheduler
    _scheduler = scheduler
    return scheduler
