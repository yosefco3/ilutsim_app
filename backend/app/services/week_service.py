"""
WeekService — business logic for schedule week management.
"""

import logging
import uuid
from datetime import date
from typing import Optional

from app.constants import WeekStatus
from app.exceptions import InvalidTransitionException, WeekLockedException
from app.models.schedule_week import ScheduleWeek
from app.repositories.schedule_week_repository import ScheduleWeekRepository
from app.schemas.week_schemas import DayItem, WeekCreate, WeekResponse, WeekWithDaysResponse
from app.utils.date_utils import get_next_week_end, get_next_week_start, week_range


logger = logging.getLogger("ilutzim")

# Allowed week-status transitions: open → locked → published.
# Admin can also reopen a locked week: locked → open.
ALLOWED_TRANSITIONS: dict[str, list[str]] = {
    "closed": ["open"],
    "open": ["locked"],
    "locked": ["open", "published"],
    "published": [],  # terminal state
}


class WeekService:
    """Orchestrates schedule week lifecycle."""

    def __init__(self, week_repo: ScheduleWeekRepository, user_repo=None) -> None:
        self._week_repo = week_repo
        self._user_repo = user_repo

    async def create_week(self, data: WeekCreate) -> WeekResponse:
        """Create a new schedule week."""
        logger.info(f"Creating week: {data.start_date} to {data.end_date}")
        week = ScheduleWeek(
            start_date=data.start_date,
            end_date=data.end_date,
            status=WeekStatus.CLOSED,
        )
        created = await self._week_repo.save(week)
        logger.info(f"Week created: id={created.id}")
        return WeekResponse.model_validate(created)

    async def get_all_weeks(self) -> list[WeekResponse]:
        """Return all schedule weeks, after the automatic weekly advance."""
        await self.auto_advance_weeks()
        weeks = await self._week_repo.get_all()
        return [WeekResponse.model_validate(w) for w in weeks]

    async def change_week_status(
        self, week_id: uuid.UUID, new_status: WeekStatus, notify: bool = True
    ) -> WeekResponse:
        """Transition a week to a new status.

        Validates that the transition follows the allowed path:
        open → locked → published.

        ``notify`` controls the Telegram broadcast. Manual admin transitions
        notify guards; the automatic Saturday-night rollover locks silently
        (``notify=False``) to avoid a midnight broadcast.
        """
        week = await self._get_week_or_raise(week_id)
        old_status = week.status

        # Reject same-status (no-op)
        if old_status == new_status:
            allowed = ", ".join(ALLOWED_TRANSITIONS.get(old_status, []))
            raise InvalidTransitionException(
                f"לא ניתן לשנות סטטוס מ-{old_status} ל-{new_status}."
                f" מעברים אפשריים: {allowed or 'אין'}"
            )

        # Validate transition is in the allowed list
        allowed_next = ALLOWED_TRANSITIONS.get(old_status, [])
        if new_status not in allowed_next:
            allowed_str = ", ".join(allowed_next) if allowed_next else "אין"
            raise InvalidTransitionException(
                f"לא ניתן לשנות סטטוס מ-{old_status} ל-{new_status}."
                f" מעברים אפשריים: {allowed_str}"
            )

        updated = await self._week_repo.update(week.id, status=new_status)
        logger.info(f"Week {week_id}: {old_status} -> {new_status}")

        # Send Telegram notifications on status change (skipped for silent
        # automatic transitions, e.g. the Saturday-night auto-lock).
        if notify:
            try:
                from app.bot.notifications import notify_week_locked, notify_week_opened, notify_week_published

                telegram_ids: list[int] = []
                if self._user_repo is not None:
                    users = await self._user_repo.get_all()
                    telegram_ids = [u.telegram_id for u in users if u.telegram_id]

                if telegram_ids:
                    if new_status == WeekStatus.OPEN:
                        await notify_week_opened(updated.start_date, updated.end_date, telegram_ids)
                    elif new_status == WeekStatus.LOCKED:
                        await notify_week_locked(updated.start_date, updated.end_date, telegram_ids)
                    elif new_status == WeekStatus.PUBLISHED:
                        await notify_week_published(updated.start_date, updated.end_date, telegram_ids)
            except Exception as exc:
                logger.warning(f"Failed to send status-change notification: {exc}")

        # Auto-create next week when publishing
        if new_status == WeekStatus.PUBLISHED:
            try:
                next_week = await self._ensure_next_week(updated)
                logger.info(
                    f"Auto-created next week: {next_week.start_date} – "
                    f"{next_week.end_date} (id={next_week.id})"
                )
            except Exception as exc:
                logger.warning(f"Failed to auto-create next week: {exc}")

        return WeekResponse.model_validate(updated)

    async def get_week(self, week_id: uuid.UUID) -> WeekResponse:
        """Return a single week by ID."""
        week = await self._get_week_or_raise(week_id)
        return WeekResponse.model_validate(week)

    async def get_current_open_week(self) -> Optional[WeekResponse]:
        """Return the currently open week, if any."""
        week = await self._week_repo.get_current_open_week()
        if week is None:
            return None
        return WeekResponse.model_validate(week)

    async def get_relevant_week_with_days(self) -> Optional[WeekWithDaysResponse]:
        """Return the week guards should see, with its status.

        Resolution order (most relevant to the guard first):
          1. The OPEN week — where they can actually submit.
          2. The nearest week that has not ended yet (``end_date >= today``),
             so a locked *current* week wins over an already-created next week.
          3. The latest week overall — when every week has ended, show the most
             recent one (typically a published schedule).

        Returns ``None`` only when no week exists at all. The UI uses the status
        to render the right banner instead of a generic "no week" error.
        """
        week = await self._week_repo.get_current_open_week()
        if week is None:
            week = await self._week_repo.get_current_or_upcoming_week(date.today())
        if week is None:
            week = await self._week_repo.get_latest_week()
        if week is None:
            return None
        days = [DayItem(day_index=i, blocked=False) for i in range(7)]
        return WeekWithDaysResponse(
            id=week.id,
            start_date=week.start_date,
            end_date=week.end_date,
            status=week.status,
            days=days,
        )

    async def get_latest_week(self) -> Optional[WeekResponse]:
        """Return the most recent week (by start_date), regardless of status."""
        week = await self._week_repo.get_latest_week()
        if week is None:
            return None
        return WeekResponse.model_validate(week)

    async def validate_week_is_open(self, week_id: uuid.UUID) -> None:
        """Raise WeekLockedException if the week is not open."""
        week = await self._get_week_or_raise(week_id)
        if week.status != WeekStatus.OPEN:
            logger.warning(f"Week {week_id} is {week.status}, not open")
            raise WeekLockedException()

    async def delete_week(self, week_id: uuid.UUID) -> None:
        """Delete a schedule week by ID.

        Only allows deletion of non-published weeks to preserve history.
        """
        week = await self._get_week_or_raise(week_id)
        if week.status == WeekStatus.PUBLISHED:
            raise InvalidTransitionException(
                "לא ניתן למחוק שבוע שפורסם — הוא חלק מההיסטוריה"
            )
        deleted = await self._week_repo.delete(week_id)
        if not deleted:
            from app.exceptions import UserNotFoundException
            raise UserNotFoundException()
        logger.info(f"Week {week_id} deleted (was {week.status})")

    async def auto_advance_weeks(self) -> None:
        """Perform the automatic weekly rollover (idempotent, self-healing).

        This is the single entry point for the Saturday-night (Motzaei Shabbat,
        Sunday 00:00) rollover. It runs on a scheduled trigger, on startup, and
        on every weeks-list load, and converges to the correct state regardless
        of how many times it runs:

          1. Lock any OPEN week whose ``start_date`` has arrived — it is the
             week that just became "current" and is no longer a relevant
             submission target (``lock_expired_open_weeks``).
          2. Ensure the upcoming Sun–Sat week exists as CLOSED so the admin has
             a next week ready to open (``auto_rotate_weeks``).
          3. Purge weeks older than the retention window so the database keeps
             only the most recent ``RETENTION_WEEKS`` weeks (``purge_old_weeks``).

        Because the lock rule keys on ``start_date <= today``, a missed run
        (server down at midnight) is corrected automatically on the next call —
        no catch-up bookkeeping needed.
        """
        await self.lock_expired_open_weeks()
        await self.auto_rotate_weeks()
        await self.purge_old_weeks()

    async def lock_expired_open_weeks(self) -> None:
        """Auto-lock OPEN weeks whose submission window has already begun.

        An open submission week is meant to be a future week. The moment its
        ``start_date`` arrives it is no longer relevant, so it is transitioned
        OPEN → LOCKED **silently** (no Telegram broadcast at midnight). The
        admin's manual lock/publish flow is untouched: a week that was already
        locked/published, or an open *future* week, is never affected.
        """
        today = date.today()
        try:
            stale = await self._week_repo.get_open_weeks_started_on_or_before(today)
        except Exception as exc:
            logger.warning(f"Failed to query expired open weeks: {exc}")
            return

        for week in stale:
            try:
                await self.change_week_status(
                    week.id, WeekStatus.LOCKED, notify=False
                )
                logger.info(
                    f"Auto-locked expired open week {week.start_date} – "
                    f"{week.end_date} (id={week.id})"
                )
            except Exception as exc:
                logger.warning(f"Failed to auto-lock week {week.id}: {exc}")

    async def auto_rotate_weeks(self) -> None:
        """Ensure the upcoming week always exists, created CLOSED.

        Runs on every weeks-list load and on startup. It does NOT change the
        status of existing weeks — every transition (open / lock / publish) is a
        deliberate admin action. Its single job: if no week exists yet for the
        upcoming Sun–Sat range, create it as CLOSED so the admin always has a
        next week ready to open.

        Dedup is by date range (``get_by_date_range``), so it never duplicates a
        week already created by ``_ensure_next_week`` after a publish.
        """
        today = date.today()
        ws, we = week_range(today)  # upcoming Sunday..Saturday

        try:
            existing = await self._week_repo.get_by_date_range(ws, we)
            if existing is None:
                new_week = ScheduleWeek(
                    start_date=ws,
                    end_date=we,
                    status=WeekStatus.CLOSED,
                )
                created = await self._week_repo.save(new_week)
                logger.info(
                    f"Auto-created upcoming week (closed): {ws} – {we} (id={created.id})"
                )
        except Exception as exc:
            logger.warning(f"Failed to auto-create upcoming week: {exc}")

    async def purge_old_weeks(self) -> int:
        """Delete weeks older than the retention window. Returns the count purged.

        Keeps only the most recent ``RETENTION_WEEKS`` weeks (by ``start_date``)
        and hard-deletes everything older — **including published weeks**, since
        the whole point of the retention cap is to bound how much history is
        kept. Children (submissions → daily statuses → shift windows) are removed
        by the ``ON DELETE CASCADE`` chain at the database level.

        Idempotent and self-healing: once the DB holds ≤ retention weeks it is a
        no-op, so it is safe to run on every rollover / weeks-list load. Failures
        are logged and swallowed so they never break the rollover.
        """
        from app.config import get_settings

        settings = get_settings()
        if not settings.RETENTION_ENABLED:
            return 0

        try:
            stale = await self._week_repo.get_weeks_beyond_retention(
                settings.RETENTION_WEEKS
            )
        except Exception as exc:
            logger.warning(f"Failed to query weeks beyond retention: {exc}")
            return 0

        purged = 0
        for week in stale:
            try:
                # Delete directly (not delete_week) to bypass the published guard:
                # purging old history is the intended behavior here.
                deleted = await self._week_repo.delete(week.id)
                if deleted:
                    purged += 1
                    logger.info(
                        f"Purged old week {week.start_date} – {week.end_date} "
                        f"(id={week.id}, was {week.status})"
                    )
            except Exception as exc:
                logger.warning(f"Failed to purge week {week.id}: {exc}")

        if purged:
            logger.info(
                f"Retention purge removed {purged} week(s); "
                f"keeping the most recent {settings.RETENTION_WEEKS}"
            )
        return purged

    # ── Internal helpers ──────────────────────────────────────────────────

    async def _ensure_next_week(self, week: ScheduleWeek) -> ScheduleWeek:
        """Auto-create the next schedule week (closed) after publish.

        Returns the newly created week.  Silently skips if one already exists.
        """
        next_start = get_next_week_start(week.start_date)
        next_end = get_next_week_end(next_start)

        existing = await self._week_repo.get_by_date_range(next_start, next_end)
        if existing is not None:
            logger.info(f"Next week already exists: {next_start} – {next_end}")
            return existing

        next_week = ScheduleWeek(
            start_date=next_start,
            end_date=next_end,
            status=WeekStatus.CLOSED,
        )
        return await self._week_repo.save(next_week)

    async def _get_week_or_raise(self, week_id: uuid.UUID) -> ScheduleWeek:
        """Fetch week or raise WeekLockedException as a proxy for not-found."""
        week = await self._week_repo.get_by_id(week_id)
        if week is None:
            from app.exceptions import UserNotFoundException
            raise UserNotFoundException()
        return week