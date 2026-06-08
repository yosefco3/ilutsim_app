"""
WeekService — business logic for schedule week management.
"""

import logging
import uuid
from datetime import date
from typing import Optional

from app.constants import WeekStatus
from app.exceptions import ConflictException, InvalidTransitionException, WeekLockedException
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
            status=WeekStatus.OPEN,
        )
        created = await self._week_repo.save(week)
        logger.info(f"Week created: id={created.id}")
        return WeekResponse.model_validate(created)

    async def get_all_weeks(self) -> list[WeekResponse]:
        """Return all schedule weeks, after auto-rotating expired ones."""
        await self.auto_rotate_weeks()
        weeks = await self._week_repo.get_all()
        return [WeekResponse.model_validate(w) for w in weeks]

    async def change_week_status(
        self, week_id: uuid.UUID, new_status: WeekStatus
    ) -> WeekResponse:
        """Transition a week to a new status.

        Validates that the transition follows the allowed path:
        open → locked → published.
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

        # Send Telegram notifications on status change
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

    async def get_current_open_week_with_days(self) -> Optional[WeekWithDaysResponse]:
        """Return the currently open week with 7 days for the submission form."""
        week = await self._week_repo.get_current_open_week()
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

    async def open_new_week(self, start_date: Optional[date] = None) -> WeekResponse:
        """Open the next schedule week.

        Refuses if a week is already open (returns 409 Conflict).
        If *start_date* is None the upcoming Sunday is used.
        """
        existing = await self._week_repo.get_current_open_week()
        if existing is not None:
            raise ConflictException("שבוע פתוח כבר קיים — יש לסגור אותו קודם")

        if start_date is None:
            start_date = date.today()
        ws, we = week_range(start_date)

        week = ScheduleWeek(start_date=ws, end_date=we, status=WeekStatus.OPEN)
        created = await self._week_repo.save(week)
        logger.info(f"New week opened automatically: {ws} – {we} (id={created.id})")

        # Notify all guards via Telegram
        try:
            from app.bot.notifications import notify_week_opened

            telegram_ids: list[int] = []
            if self._user_repo is not None:
                users = await self._user_repo.get_all()
                telegram_ids = [u.telegram_id for u in users if u.telegram_id]

            if telegram_ids:
                notified = await notify_week_opened(ws, we, telegram_ids)
                logger.info(f"Week-open notification delivered to {notified}/{len(telegram_ids)} guards")
        except Exception as exc:
            logger.warning(f"Failed to send week-open notifications: {exc}")

        return WeekResponse.model_validate(created)

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

    async def auto_rotate_weeks(self) -> None:
        """Auto-rotate expired weeks and create next week if needed.

        For any week whose end_date < today and is not yet PUBLISHED:
          - Set status to PUBLISHED (archive it).
        If no open week exists for the current period:
          - Create a new OPEN week for the upcoming schedule period.
        """
        from sqlalchemy import select

        today = date.today()

        # Find expired weeks (end_date < today) that are not PUBLISHED
        all_weeks = await self._week_repo.get_all()
        rotated_any = False

        for week in all_weeks:
            if week.end_date < today and week.status != WeekStatus.PUBLISHED:
                old_status = week.status
                await self._week_repo.update(week.id, status=WeekStatus.PUBLISHED)
                logger.info(
                    f"Auto-rotated expired week {week.id} "
                    f"({week.start_date} – {week.end_date}): "
                    f"{old_status} → PUBLISHED"
                )
                rotated_any = True

        # If no current open week, create one for the upcoming period
        current_open = await self._week_repo.get_current_open_week()
        if current_open is None:
            try:
                ws, we = week_range(today)
                # Check if a week for this range already exists
                existing = await self._week_repo.get_by_date_range(ws, we)
                if existing is None:
                    new_week = ScheduleWeek(
                        start_date=ws,
                        end_date=we,
                        status=WeekStatus.OPEN,
                    )
                    created = await self._week_repo.save(new_week)
                    logger.info(
                        f"Auto-created new open week: {ws} – {we} (id={created.id})"
                    )
            except Exception as exc:
                logger.warning(f"Failed to auto-create current week: {exc}")

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