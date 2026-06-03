"""Schedule week schemas with date range validation."""

import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict, model_validator

from app.constants import WeekStatus
from app.messages import Messages


class WeekCreate(BaseModel):
    """Schema for creating a schedule week."""
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_date_range(self) -> "WeekCreate":
        if self.end_date <= self.start_date:
            raise ValueError(Messages.VAL_DATE_RANGE)
        return self


class WeekStatusUpdate(BaseModel):
    """Schema for updating week status."""
    status: WeekStatus


class WeekResponse(BaseModel):
    """Schema for week data in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    start_date: date
    end_date: date
    status: WeekStatus