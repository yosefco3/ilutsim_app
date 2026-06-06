"""
ScheduleWeek repository — data access for weekly schedule periods.
"""

import uuid
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import WeekStatus
from app.models.schedule_week import ScheduleWeek
from app.repositories.base_repository import BaseRepository


class ScheduleWeekRepository(BaseRepository[ScheduleWeek]):
    """Data-access operations for ScheduleWeek entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ScheduleWeek)

    async def get_current_open_week(self) -> ScheduleWeek | None:
        """Return the week whose status is OPEN."""
        stmt = select(self.model_class).where(ScheduleWeek.status == WeekStatus.OPEN)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_date_range(self, start: date, end: date) -> ScheduleWeek | None:
        """Find a week that exactly matches the given date range."""
        stmt = select(self.model_class).where(
            ScheduleWeek.start_date == start,
            ScheduleWeek.end_date == end,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count(self) -> int:
        """Return the total number of weeks."""
        result = await self.session.execute(select(func.count(ScheduleWeek.id)))
        return result.scalar()

    async def update_status(
        self, week_id: uuid.UUID, new_status: WeekStatus
    ) -> ScheduleWeek:
        """Transition a week to a new status."""
        return await self.update(week_id, status=new_status)
