"""Schedule event schemas with date validation."""

import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict, model_validator

from app.constants import EventType
from app.messages import Messages


class ScheduleEventCreate(BaseModel):
    """Schema for creating a schedule event."""
    user_id: uuid.UUID
    event_type: EventType
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_date_range(self) -> "ScheduleEventCreate":
        if self.end_date < self.start_date:
            raise ValueError(Messages.VAL_DATE_RANGE_SAME_OK)
        return self


class ScheduleEventResponse(BaseModel):
    """Schema for event data in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    event_type: EventType
    start_date: date
    end_date: date


class BlockedDateInfo(BaseModel):
    """Info about a blocked date for a user."""
    date: date
    event_type: EventType
    label: str