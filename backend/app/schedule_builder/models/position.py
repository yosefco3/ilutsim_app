"""
Position model — part B (schedule builder).

A *position* (עמדה) is one row in the schedule = a requirement for **one** guard.
Two guards at the same physical spot = two positions. A position belongs to an
``ActivationProfile`` and carries:

- ``shift``               — MORNING / AFTERNOON (=ערב) / NIGHT
- ``day_schedules``       — per-day hours AND active-days in one JSON map:
                            ``{"0": {"start": "07:30", "end": "15:00"}, ...}``.
                            A day index present = that day is active; missing =
                            inactive. Day index 0=ראשון … 6=שבת. A night window
                            where ``end <= start`` wraps past midnight (the part-A
                            convention).
- ``required_attributes`` — list of attribute *keys* (e.g. ``["armed", "roni"]``)
                            referencing the configurable RequirementAttribute
                            vocabulary. The link is **soft** (no hard FK), so the
                            vocabulary can change without breaking positions.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import ShiftType
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.schedule_builder.models.activation_profile import ActivationProfile

# Postgres stores these as JSONB; SQLite (tests) falls back to generic JSON.
JSONType = JSON().with_variant(JSONB(), "postgresql")


class Position(BaseModel):
    """One schedule row = a requirement for a single guard."""

    # Owning profile. nullable=False but **updatable** — moving a position
    # between profiles = reassigning this FK. CASCADE: deleting a profile
    # deletes its positions.
    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("activation_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Display name (e.g. "ארנונה", "קומה 6", "סייר 1").
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Which shift this position belongs to. Reuses the part-A ``shift_type`` enum.
    shift: Mapped[ShiftType] = mapped_column(
        Enum(ShiftType, name="shift_type"), nullable=False,
    )

    # Per-day hours + active days in one map: day index ("0".."6") -> {start,end}.
    # Presence of a key = active that day; missing = inactive.
    day_schedules: Mapped[dict] = mapped_column(
        JSONType, nullable=False, default=dict, server_default="{}",
    )

    # Required attribute keys (soft reference to RequirementAttribute vocabulary).
    required_attributes: Mapped[list] = mapped_column(
        JSONType, nullable=False, default=list, server_default="[]",
    )

    # Display order within the owning profile.
    display_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0",
    )

    profile: Mapped["ActivationProfile"] = relationship(back_populates="positions")
