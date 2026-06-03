"""
ScheduleEvent model — guard blockout events (vacation, military, etc.).
"""

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import EventType
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


class ScheduleEvent(BaseModel):
    """Guard availability blockout event."""

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False,
    )
    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType, name="event_type"), nullable=False,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="schedule_events")
