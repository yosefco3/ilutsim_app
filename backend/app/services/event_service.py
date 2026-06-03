"""
EventService — business logic for schedule events (vacation, military, etc.).
"""

import logging
import uuid
from typing import Optional

from app.constants import EventType
from app.exceptions import UserNotFoundException, ValidationException
from app.messages import Messages
from app.models.schedule_event import ScheduleEvent
from app.repositories.schedule_event_repository import ScheduleEventRepository
from app.repositories.user_repository import UserRepository
from app.schemas.event_schemas import EventCreate, EventResponse

logger = logging.getLogger("ilutzim")


class EventService:
    """Orchestrates schedule event CRUD and validation."""

    def __init__(
        self,
        event_repo: ScheduleEventRepository,
        user_repo: UserRepository,
    ) -> None:
        self._event_repo = event_repo
        self._user_repo = user_repo

    async def create_event(self, data: EventCreate) -> EventResponse:
        """Create a new schedule event after validation."""
        # Validate user exists
        user = await self._user_repo.get_by_id(data.user_id)
        if user is None:
            raise UserNotFoundException()

        # Validate date range
        if data.end_date < data.start_date:
            raise ValidationException(Messages.VAL_DATE_RANGE)

        event = ScheduleEvent(
            user_id=data.user_id,
            event_type=data.event_type,
            start_date=data.start_date,
            end_date=data.end_date,
            notes=data.notes,
        )
        created = await self._event_repo.create(event)
        logger.info(f"Event created: user={data.user_id}, type={data.event_type}")
        return EventResponse.model_validate(created)

    async def get_events_for_user(
        self, user_id: uuid.UUID
    ) -> list[EventResponse]:
        """Return all events for a user."""
        events = await self._event_repo.get_by_user(user_id)
        return [EventResponse.model_validate(e) for e in events]

    async def delete_event(self, event_id: uuid.UUID) -> bool:
        """Delete an event by ID."""
        deleted = await self._event_repo.delete(event_id)
        if deleted:
            logger.info(f"Event deleted: {event_id}")
        return deleted