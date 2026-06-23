"""
ScheduleWeek model — represents a weekly scheduling period.
"""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum
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
    # Set the first time the week enters OPEN. NULL = never opened, which is how
    # the auto-open cron distinguishes a fresh week from one whose submission
    # window already ran (now CLOSED again) — so it is never auto-reopened.
    opened_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    weekly_submissions: Mapped[list["WeeklySubmission"]] = relationship(
        back_populates="week", cascade="all, delete-orphan",
        passive_deletes=True,
    )