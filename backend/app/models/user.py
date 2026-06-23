"""
User model — security guards.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import UserRole
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.weekly_submission import WeeklySubmission


class User(BaseModel):
    """Security guard profile."""

    phone_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False,
    )
    telegram_id: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True,
    )
    first_name: Mapped[str] = mapped_column(
        String(50), nullable=False,
    )
    last_name: Mapped[str] = mapped_column(
        String(50), nullable=False,
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True,
    )
    exemptions_notes: Mapped[str | None] = mapped_column(
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
    weekly_submissions: Mapped[list["WeeklySubmission"]] = relationship(
        back_populates="user", cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_users_phone_number", "phone_number"),
        Index("ix_users_telegram_id", "telegram_id"),
    )