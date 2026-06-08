"""Submission schemas — core shift/availability validation."""

import uuid
from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.constants import ShiftType, SubmissionStatus
from app.messages import Messages


# ── Guard-side (Telegram WebApp) schemas ────────────────────────────────────

class GuardShiftInput(BaseModel):
    """Single shift as submitted by a guard — raw time strings."""
    shift_type: ShiftType
    from_hour: str | None = None  # "HH:MM"
    to_hour: str | None = None    # "HH:MM"


class GuardDayInput(BaseModel):
    """Single day entry in a guard's weekly submission."""
    day_index: int = Field(ge=0, le=6)
    shifts: list[GuardShiftInput] = []


class GuardSubmissionRequest(BaseModel):
    """Payload sent by the guard's frontend via POST /submissions."""
    week_id: uuid.UUID
    general_notes: str | None = None
    days: list[GuardDayInput]

    @model_validator(mode="after")
    def validate_days_not_empty(self) -> "GuardSubmissionRequest":
        if len(self.days) == 0:
            raise ValueError(Messages.VAL_EMPTY_DAYS)
        return self


# ── Internal schemas (used by service layer) ─────────────────────────────────

class ShiftWindowInput(BaseModel):
    """Schema for a single shift window within a day."""
    shift_type: ShiftType
    start_time: time
    end_time: time

    @model_validator(mode="after")
    def validate_times(self) -> "ShiftWindowInput":
        if self.start_time == self.end_time:
            raise ValueError(Messages.VAL_SAME_START_END)
        if self.shift_type == ShiftType.NIGHT:
            pass  # Night shifts can cross midnight
        elif self.start_time > self.end_time:
            raise ValueError(Messages.VAL_SAME_START_END)
        return self


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


class SubmissionCreate(BaseModel):
    """Schema for creating/updating a weekly submission."""
    week_id: uuid.UUID
    user_id: uuid.UUID
    general_notes: str | None = None
    days: list[DayStatusInput]

    @model_validator(mode="after")
    def validate_days_not_empty(self) -> "SubmissionCreate":
        if len(self.days) == 0:
            raise ValueError(Messages.VAL_EMPTY_DAYS)
        return self


# ── Response schemas ─────────────────────────────────────────────────────────

class ShiftWindowResponse(BaseModel):
    """Schema for shift window in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    shift_type: ShiftType
    start_time: time
    end_time: time


class DayStatusResponse(BaseModel):
    """Schema for day status in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    date: date
    is_available: bool
    shift_windows: list[ShiftWindowResponse] = []


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