"""
ScheduleEvent repository — data access for guard blockout events.
"""

import uuid
from datetime import date

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import EventType
from app.models.schedule_event import ScheduleEvent
from app.repositories.base_repository import BaseRepository


class ScheduleEventRepository(BaseRepository[ScheduleEvent]):
    """Data-access operations for ScheduleEvent entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ScheduleEvent)

    async def get_events_for_user(
        self, user_id: uuid.UUID, start_date: date, end_date: date
    ) -> list[ScheduleEvent]:
        """Return events for a user that overlap the given date range.

        Overlap condition: event.start_date <= end AND event.end_date >= start
        """
        stmt = select(self.model_class).where(
            ScheduleEvent.user_id == user_id,
            ScheduleEvent.start_date <= end_date,
            ScheduleEvent.end_date >= start_date,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_full_week_absences(
        self, week_start: date, week_end: date
    ) -> list[ScheduleEvent]:
        """Return events that cover the entire week.

        An event covers the full week when:
            start_date <= week_start AND end_date >= week_end
        """
        stmt = select(self.model_class).where(
            ScheduleEvent.start_date <= week_start,
            ScheduleEvent.end_date >= week_end,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_event(
        self,
        user_id: uuid.UUID,
        event_type: EventType,
        start: date,
        end: date,
    ) -> ScheduleEvent:
        """Create a new blockout event."""
        return await self.create(
            user_id=user_id,
            event_type=event_type,
            start_date=start,
            end_date=end,
        )

    async def delete_event(self, event_id: uuid.UUID) -> bool:
        """Delete an event by ID."""
        return await self.delete(event_id)