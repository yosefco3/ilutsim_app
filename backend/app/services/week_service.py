"""
WeekService — business logic for schedule week management.
"""

import logging
import uuid
from datetime import date
from typing import Optional

from app.constants import WeekStatus
from app.exceptions import ConflictException, WeekLockedException
from app.models.schedule_week import ScheduleWeek
from app.repositories.schedule_week_repository import ScheduleWeekRepository
from app.schemas.week_schemas import WeekCreate, WeekResponse
from app.utils.date_utils import week_range

logger = logging.getLogger("ilutzim")


class WeekService:
    """Orchestrates schedule week lifecycle."""

    def __init__(self, week_repo: ScheduleWeekRepository) -> None:
        self._week_repo = week_repo

    async def create_week(self, data: WeekCreate) -> WeekResponse:
        """Create a new schedule week."""
        logger.info(f"Creating week: {data.start_date} to {data.end_date}")
        week = ScheduleWeek(
            start_date=data.start_date,
            end_date=data.end_date,
            status=WeekStatus.OPEN,
        )
        created = await self._week_repo.create(week)
        logger.info(f"Week created: id={created.id}")
        return WeekResponse.model_validate(created)

    async def get_all_weeks(self) -> list[WeekResponse]:
        """Return all schedule weeks."""
        weeks = await self._week_repo.get_all()
        return [WeekResponse.model_validate(w) for w in weeks]

    async def change_week_status(
        self, week_id: uuid.UUID, new_status: WeekStatus
    ) -> WeekResponse:
        """Transition a week to a new status."""
        week = await self._get_week_or_raise(week_id)
        old_status = week.status
        week.status = new_status
        updated = await self._week_repo.update(week)
        logger.info(f"Week {week_id}: {old_status} -> {new_status}")
        return WeekResponse.model_validate(updated)

    async def get_current_open_week(self) -> Optional[WeekResponse]:
        """Return the currently open week, if any."""
        week = await self._week_repo.get_current_open_week()
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
        created = await self._week_repo.create(week)
        logger.info(f"New week opened automatically: {ws} – {we} (id={created.id})")
        return WeekResponse.model_validate(created)

    # ── Internal helpers ──────────────────────────────────────────────────

    async def _get_week_or_raise(self, week_id: uuid.UUID) -> ScheduleWeek:
        """Fetch week or raise WeekLockedException as a proxy for not-found."""
        week = await self._week_repo.get_by_id(week_id)
        if week is None:
            from app.exceptions import UserNotFoundException
            raise UserNotFoundException()
        return week