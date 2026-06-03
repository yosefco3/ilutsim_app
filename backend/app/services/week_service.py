"""
WeekService — business logic for schedule week management.
"""

import logging
import uuid
from typing import Optional

from app.constants import WeekStatus
from app.exceptions import WeekLockedException
from app.models.schedule_week import ScheduleWeek
from app.repositories.schedule_week_repository import ScheduleWeekRepository
from app.schemas.week_schemas import WeekCreate, WeekResponse

logger = logging.getLogger("ilutzim")


class WeekService:
    """Orchestrates schedule week lifecycle."""

    def __init__(self, week_repo: ScheduleWeekRepository) -> None:
        self._week_repo = week_repo

    async def create_week(self, data: WeekCreate) -> WeekResponse:
        """Create a new schedule week."""
        logger.info(f"Creating week: {data.week_start} to {data.week_end}")
        week = ScheduleWeek(
            week_start=data.week_start,
            week_end=data.week_end,
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

    # ── Internal helpers ──────────────────────────────────────────────────

    async def _get_week_or_raise(self, week_id: uuid.UUID) -> ScheduleWeek:
        """Fetch week or raise WeekLockedException as a proxy for not-found."""
        week = await self._week_repo.get_by_id(week_id)
        if week is None:
            from app.exceptions import UserNotFoundException
            raise UserNotFoundException()
        return week