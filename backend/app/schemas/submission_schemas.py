"""Submission schemas — core shift/availability validation."""

import uuid
from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.constants import ShiftType, SubmissionStatus
from app.messages import Messages


class ShiftWindowInput(BaseModel):
    """Schema for a single shift window within a day."""
    shift_type: ShiftType
    start_time: time
    end_time: time

    @model_validator(mode="after")
    def validate_times(self) -> "ShiftWindowInput":
        # Same start and end is never valid
        if self.start_time == self.end_time:
            raise ValueError(Messages.VAL_SAME_START_END)

        # Night shifts can cross midnight (start > end is valid, e.g. 23:00-07:00)
        if self.shift_type == ShiftType.NIGHT:
            pass  # Both start < end and start > end are valid for night
        else:
            # For morning/afternoon, start must be before end
            if self.start_time > self.end_time:
                raise ValueError(Messages.VAL_SAME_START_END)

        return self


class ShiftWindowResponse(BaseModel):
    """Schema for shift window in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    shift_type: ShiftType
    start_time: time
    end_time: time


class DayStatusInput(BaseModel):
    """Schema for a single day's availability and shifts."""
    date: date
    is_available: bool
    shifts: list[ShiftWindowInput] = []

    @model_validator(mode="after")
    def validate_shifts_availability(self) -> "DayStatusInput":
        if not self.is_available and len(self.shifts) > 0:
            raise ValueError(Messages.VAL_UNAVAILABLE_WITH_SHIFTS)
        if self.is_available and len(self.shifts) == 0:
            raise ValueError(Messages.VAL_AVAILABLE_NO_SHIFTS)
        return self


class DayStatusResponse(BaseModel):
    """Schema for day status in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    date: date
    is_available: bool
    shift_windows: list[ShiftWindowResponse] = []


class SubmissionCreate(BaseModel):
    """Schema for creating/updating a weekly submission."""
    week_id: uuid.UUID
    general_notes: str | None = None
    days: list[DayStatusInput]

    @model_validator(mode="after")
    def validate_days_not_empty(self) -> "SubmissionCreate":
        if len(self.days) == 0:
            raise ValueError(Messages.VAL_EMPTY_DAYS)
        return self


class SubmissionResponse(BaseModel):
    """Schema for submission data in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    week_id: uuid.UUID
    status: SubmissionStatus
    general_notes: str | None = None
    has_deviation: bool = False
    submitted_at: datetime
    days: list[DayStatusResponse] = []


class SubmissionStatusGrid(BaseModel):
    """Grid row showing a user's submission status for a week."""
    user_id: uuid.UUID
    full_name: str
    phone_number: str
    status: SubmissionStatus
    submitted_at: datetime | None = None
    has_deviation: bool = False


class DeviationDetail(BaseModel):
    """Detail of a single deviation rule violation."""
    rule_name: str
    required: int
    actual: int