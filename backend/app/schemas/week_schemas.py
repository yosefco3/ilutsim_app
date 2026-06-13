"""Schedule week schemas with date range validation."""

import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict, computed_field, model_validator

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
    # Number of guards who submitted for this week. Populated by the weeks
    # endpoint (defaults to 0 so single-week responses stay valid).
    submission_count: int = 0

    @computed_field
    @property
    def week_label(self) -> str:
        """Human-readable week label, e.g. 'שבוע 01/06 - 07/06'."""
        return f"שבוע {self.start_date.strftime('%d/%m')} – {self.end_date.strftime('%d/%m')}"


class DayItem(BaseModel):
    """Single day in a week's submission form."""
    day_index: int
    blocked: bool = False


class WeekWithDaysResponse(WeekResponse):
    """Week data with 7 days for the submission form."""
    days: list[DayItem]
