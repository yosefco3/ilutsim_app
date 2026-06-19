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

    async def get_open_weeks_started_on_or_before(
        self, today: date
    ) -> list[ScheduleWeek]:
        """Return all OPEN weeks whose submission window has begun.

        A week that is open for submission is meant to be a *future* week. Once
        its ``start_date`` arrives (``start_date <= today``) it is no longer a
        relevant submission target and should be auto-locked. Returns a list
        (normally 0 or 1) ordered by start_date so the auto-advance can lock
        every stale open week deterministically.
        """
        stmt = (
            select(self.model_class)
            .where(
                ScheduleWeek.status == WeekStatus.OPEN,
                ScheduleWeek.start_date <= today,
            )
            .order_by(ScheduleWeek.start_date.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_date_range(self, start: date, end: date) -> ScheduleWeek | None:
        """Find a week that exactly matches the given date range."""
        stmt = select(self.model_class).where(
            ScheduleWeek.start_date == start,
            ScheduleWeek.end_date == end,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_current_or_upcoming_week(self, today: date) -> ScheduleWeek | None:
        """Return the nearest week that has not ended yet (``end_date >= today``).

        Ordered by start_date ascending, so the *current* cycle wins over a
        later already-created week. Used to show the guard the week they most
        recently acted on (e.g. a locked current week) rather than next week.
        """
        stmt = (
            select(self.model_class)
            .where(ScheduleWeek.end_date >= today)
            .order_by(ScheduleWeek.start_date.asc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_upcoming_closed_week(self, today: date) -> ScheduleWeek | None:
        """Return the nearest CLOSED week that has not ended yet.

        This is the next week the admin (or the auto-open cron) would open for
        submissions. Ordered by start_date ascending so the soonest candidate
        wins.
        """
        stmt = (
            select(self.model_class)
            .where(
                ScheduleWeek.status == WeekStatus.CLOSED,
                ScheduleWeek.end_date >= today,
            )
            .order_by(ScheduleWeek.start_date.asc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_latest_week(self) -> ScheduleWeek | None:
        """Return the most recent week (by start_date), regardless of status."""
        stmt = (
            select(self.model_class)
            .order_by(ScheduleWeek.start_date.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count(self) -> int:
        """Return the total number of weeks."""
        result = await self.session.execute(select(func.count(ScheduleWeek.id)))
        return result.scalar()

    async def get_weeks_beyond_retention(self, keep: int) -> list[ScheduleWeek]:
        """Return weeks older than the ``keep`` most-recent ones (purge candidates).

        Weeks are ordered by ``start_date`` descending and the first ``keep`` are
        retained; everything past that offset is returned for deletion. A
        non-positive ``keep`` returns an empty list (safety — never purge all).
        """
        if keep <= 0:
            return []
        stmt = (
            select(self.model_class)
            .order_by(ScheduleWeek.start_date.desc())
            .offset(keep)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(
        self, week_id: uuid.UUID, new_status: WeekStatus
    ) -> ScheduleWeek:
        """Transition a week to a new status."""
        return await self.update(week_id, status=new_status)
