"""
ScheduleWeek model — represents a weekly scheduling period.
"""

from datetime import date
from typing import TYPE_CHECKING, List

from sqlalchemy import Date, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import WeekStatus
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.weekly_submission import WeeklySubmission


class ScheduleWeek(BaseModel):
    """Weekly schedule period."""

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[WeekStatus] = mapped_column(
        Enum(WeekStatus, name="week_status"),
        nullable=False,
        default=WeekStatus.OPEN,
    )

    # Relationships
    weekly_submissions: Mapped[List["WeeklySubmission"]] = relationship(
        back_populates="week", cascade="all, delete-orphan",
        passive_deletes=True,
    )