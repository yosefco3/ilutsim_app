"""
WeekService — business logic for schedule week management.
"""

import logging
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from app.constants import WeekStatus
from app.exceptions import InvalidTransitionException, WeekLockedException
from app.models.schedule_week import ScheduleWeek
from app.repositories.schedule_week_repository import ScheduleWeekRepository
from app.schemas.week_schemas import DayItem, WeekCreate, WeekResponse, WeekWithDaysResponse
from app.utils.date_utils import get_next_week_end, get_next_week_start, week_range


logger = logging.getLogger("ilutzim")

# Allowed week-status transitions (3-state model).
#
#   CLOSED = submissions closed but REOPENABLE; admin may edit on behalf of guards
#            (week creation, or the auto-lock TIME closing an OPEN week).
#   OPEN   = submissions accepted; stamps ``opened_at`` on first entry.
#   LOCKED = final, non-reopenable. Reached by the Sunday rollover (silent) or by
#            the admin "publish" action (manual lock). There is no PUBLISHED.
ALLOWED_TRANSITIONS: dict[str, list[str]] = {
    "closed": ["open", "locked"],
    "open": ["closed", "locked"],
    "locked": [],  # terminal — final, non-reopenable
}

# APScheduler day_of_week tokens → Python ``date.weekday()`` index (Mon=0 … Sun=6).
# Used to compute the weekly auto-open/auto-lock moments for the catch-up open.
_PY_WEEKDAY: dict[str, int] = {
    "mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6,
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

        Validates the transition against ALLOWED_TRANSITIONS (3-state model:
        closed ⇄ open, and either → locked; locked is terminal).

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

        # Stamp the first time a week is opened. ``opened_at`` is what tells the
        # auto-open cron a week was already opened, so it is never auto-reopened
        # after its submission window closes (which now returns it to CLOSED).
        # Re-opening a previously-opened week keeps the original timestamp.
        update_fields: dict = {"status": new_status}
        if new_status == WeekStatus.OPEN and week.opened_at is None:
            # naive UTC to match the naive ``timestamp`` column (asyncpg rejects
            # tz-aware values for ``timestamp without time zone``).
            update_fields["opened_at"] = datetime.now(timezone.utc).replace(tzinfo=None)

        updated = await self._week_repo.update(week.id, **update_fields)
        logger.info(f"Week {week_id}: {old_status} -> {new_status}")

        # Send Telegram notifications on status change (skipped for silent
        # automatic transitions, e.g. the Saturday-night auto-lock).
        if notify:
            try:
                from app.bot.notifications import notify_week_locked, notify_week_opened

                telegram_ids: list[int] = []
                if self._user_repo is not None:
                    users = await self._user_repo.get_all()
                    telegram_ids = [u.telegram_id for u in users if u.telegram_id]

                if telegram_ids:
                    if new_status == WeekStatus.OPEN:
                        await notify_week_opened(updated.start_date, updated.end_date, telegram_ids)
                    elif new_status == WeekStatus.LOCKED:
                        await notify_week_locked(updated.start_date, updated.end_date, telegram_ids)
            except Exception as exc:
                logger.warning(f"Failed to send status-change notification: {exc}")

        # A *manual* transition to LOCKED is the admin "publish" action — it
        # finalizes the schedule, so ensure the next week exists. The Sunday
        # rollover also locks weeks but with notify=False (auto_rotate already
        # creates the upcoming week), so it is excluded here to avoid double work.
        if new_status == WeekStatus.LOCKED and notify:
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

        Only allows deletion of non-finalized weeks to preserve history.
        """
        week = await self._get_week_or_raise(week_id)
        if week.status == WeekStatus.LOCKED:
            raise InvalidTransitionException(
                "לא ניתן למחוק שבוע נעול — הוא חלק מההיסטוריה"
            )
        deleted = await self._week_repo.delete(week_id)
        if not deleted:
            from app.exceptions import UserNotFoundException
            raise UserNotFoundException()
        logger.info(f"Week {week_id} deleted (was {week.status})")

    async def auto_open_relevant_week(self) -> Optional[WeekResponse]:
        """Open the upcoming closed week for submissions (cron entry point).

        Broadcasts to guards (``notify=True``). Idempotent and crash-safe:
          - if a week is already OPEN → no-op, returns ``None`` (don't open two).
          - if there is no upcoming CLOSED week → no-op (auto_rotate creates it).
          - any error is logged, never raised, so the cron job keeps running.

        Publishing stays manual — this only does closed → open.
        """
        try:
            existing_open = await self._week_repo.get_current_open_week()
            if existing_open is not None:
                logger.info(
                    "auto_open: a week is already open (id=%s) — skipping",
                    existing_open.id,
                )
                return None

            candidate = await self._week_repo.get_upcoming_closed_week(date.today())
            if candidate is None:
                logger.info("auto_open: no upcoming closed week to open — skipping")
                return None

            result = await self.change_week_status(
                candidate.id, WeekStatus.OPEN, notify=True
            )
            logger.info(
                "auto_open: opened week %s – %s (id=%s)",
                candidate.start_date,
                candidate.end_date,
                candidate.id,
            )
            return result
        except Exception as exc:
            logger.warning("auto_open_relevant_week failed: %s", exc)
            return None

    @staticmethod
    def _last_weekly_moment(
        now: datetime, weekday_token: str, hour: int, minute: int
    ) -> datetime:
        """Most recent datetime ``<= now`` on ``weekday_token`` at ``hour:minute``.

        ``weekday_token`` is an APScheduler day-of-week token ("sun".."sat").
        Used to locate the current cycle's auto-open / auto-lock boundaries.
        """
        target_wd = _PY_WEEKDAY.get(weekday_token, 6)
        delta = (now.weekday() - target_wd) % 7
        moment = (now - timedelta(days=delta)).replace(
            hour=hour, minute=minute, second=0, microsecond=0
        )
        if moment > now:  # the weekday matches today but the time hasn't arrived
            moment -= timedelta(days=7)
        return moment

    @staticmethod
    def _is_in_open_phase(now: datetime, auto_open: dict, auto_lock: dict) -> bool:
        """Whether ``now`` is inside the weekly window the target week should be OPEN.

        We are in the open phase when the most recent auto-open moment is more
        recent than the most recent auto-lock moment (the latest boundary we
        crossed was an open, not a lock). With auto-lock disabled the week stays
        open until the Sunday rollover, so any time after an auto-open counts.
        Returns False when auto-open is disabled.
        """
        if not auto_open.get("enabled"):
            return False
        open_moment = WeekService._last_weekly_moment(
            now, auto_open["weekday"], auto_open["hour"], auto_open["minute"]
        )
        if auto_lock.get("enabled"):
            lock_moment = WeekService._last_weekly_moment(
                now, auto_lock["weekday"], auto_lock["hour"], auto_lock["minute"]
            )
            return open_moment > lock_moment
        return True

    async def auto_open_if_due(self) -> Optional[WeekResponse]:
        """Catch-up auto-open for the self-heal / startup path.

        The scheduled auto-open cron fires once a week; if that single firing is
        missed (deploy, restart, or a transient failure in the 00:00 rollover
        that leaves no week for the 01:00 open to act on), nothing else opens the
        week — unlike lock/rotate/purge, which self-heal on every weeks-list load.
        This closes that gap: whenever we are inside the configured weekly open
        window and the target week is still closed, open it.

        The open window is computed in ``SCHEDULER_TIMEZONE`` (not the server's
        UTC date) so the boundary is correct across midnight. Idempotent — it
        delegates to ``auto_open_relevant_week``, which no-ops when a week is
        already OPEN or there is no never-opened candidate, so it opens (and
        broadcasts) at most once per cycle. Errors are logged, never raised.
        """
        try:
            from app.config import get_settings
            from app.repositories.system_settings_repository import (
                SystemSettingsRepository,
            )
            from app.services.settings_service import SettingsService

            settings_service = SettingsService(
                SystemSettingsRepository(self._week_repo.session)
            )
            auto_open = await settings_service.get_auto_open()
            if not auto_open.get("enabled"):
                return None
            auto_lock = await settings_service.get_auto_lock()

            now = datetime.now(ZoneInfo(get_settings().SCHEDULER_TIMEZONE))
            if not self._is_in_open_phase(now, auto_open, auto_lock):
                return None

            return await self.auto_open_relevant_week()
        except Exception as exc:
            logger.warning("auto_open_if_due failed: %s", exc)
            return None

    async def auto_lock_open_week(self) -> Optional[WeekResponse]:
        """Close the currently open week's submission window (cron entry point).

        Transitions OPEN → CLOSED (reopenable) with ``notify=False`` — the
        scheduled lock TIME ends submissions but the week stays editable by an
        admin and can be reopened; it is finalized to LOCKED only by the Sunday
        rollover. Idempotent and crash-safe: no open week → no-op; terminal
        weeks are never touched (only an OPEN week is selected); errors are
        logged, not raised. (Job id stays ``auto_lock_week`` for settings stability.)
        """
        try:
            week = await self._week_repo.get_current_open_week()
            if week is None:
                logger.info("auto_lock: no open week — skipping")
                return None

            result = await self.change_week_status(
                week.id, WeekStatus.CLOSED, notify=False
            )
            logger.info(
                "auto_lock: closed submission window for week %s – %s (id=%s)",
                week.start_date,
                week.end_date,
                week.id,
            )
            return result
        except Exception as exc:
            logger.warning("auto_lock_open_week failed: %s", exc)
            return None

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
        await self.auto_open_if_due()
        await self.purge_old_weeks()

    async def lock_expired_open_weeks(self) -> None:
        """Finalize started weeks to LOCKED at the Sunday rollover.

        The moment a week's ``start_date`` arrives it is no longer a relevant
        submission target, so the rollover finalizes it OPEN/CLOSED → LOCKED
        **silently** (no Telegram broadcast at midnight). LOCKED is the final,
        non-reopenable state. Only a week that already had its submission window
        is finalized (OPEN, or CLOSED with ``opened_at`` set); a never-opened
        CLOSED week — the upcoming/current week waiting to be opened — and
        already-LOCKED weeks are never touched.
        """
        today = date.today()
        try:
            stale = await self._week_repo.get_weeks_to_finalize_on_or_before(today)
        except Exception as exc:
            logger.warning(f"Failed to query weeks to finalize: {exc}")
            return

        for week in stale:
            try:
                await self.change_week_status(
                    week.id, WeekStatus.LOCKED, notify=False
                )
                logger.info(
                    f"Rollover finalized week {week.start_date} – "
                    f"{week.end_date} to LOCKED (id={week.id})"
                )
            except Exception as exc:
                logger.warning(f"Failed to finalize week {week.id}: {exc}")

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
        and hard-deletes everything older — **including locked/finalized weeks**, since
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
                # Delete directly (not delete_week) to bypass the locked-week guard:
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