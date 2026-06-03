"""
User model — security guards.
"""

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Enum, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import UserRole
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.schedule_event import ScheduleEvent
    from app.models.weekly_submission import WeeklySubmission


class User(BaseModel):
    """Security guard profile."""

    phone_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False,
    )
    telegram_id: Mapped[Optional[str]] = mapped_column(
        String(50), unique=True, nullable=True,
    )
    full_name: Mapped[str] = mapped_column(
        String(100), nullable=False,
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True,
    )
    exemptions_notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True,
    )
    min_total_shifts: Mapped[int] = mapped_column(
        Integer, default=0,
    )
    min_night_shifts: Mapped[int] = mapped_column(
        Integer, default=0,
    )
    min_evening_shifts: Mapped[int] = mapped_column(
        Integer, default=0,
    )

    # Relationships
    schedule_events: Mapped[List["ScheduleEvent"]] = relationship(
        back_populates="user", cascade="all, delete-orphan",
    )
    weekly_submissions: Mapped[List["WeeklySubmission"]] = relationship(
        back_populates="user", cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_users_phone_number", "phone_number"),
        Index("ix_users_telegram_id", "telegram_id"),
    )