"""
ActivationProfile model — part B (schedule builder).

An activation profile is a **reusable template** that holds positions — a "mode"
of operation (routine / holiday / event). It is NOT a per-week instance: one
"שגרה" template is reused across many weeks. The core workflow is *duplicate +
edit*: copy "שגרה", change one day, save as a new profile (e.g. a mid-week
holiday). Profile↔week binding arrives with the board (task 04).
"""

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class ActivationProfile(BaseModel):
    """Reusable schedule template that owns positions."""

    # Display name, free text (e.g. "שגרה", "חג סוכות").
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Free-text category label (e.g. "שגרה" / "חג" / "אירוע" / anything).
    # Deliberately NOT an enum — maximum flexibility (locked with the user).
    kind: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Optional free-text description.
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Marks the seeded "שגרה" profile. Exactly one profile should be True.
    is_default: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0",
    )

    # Display order in the management screen.
    display_order: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0",
    )

    # ── Future (task 03 — positions) — design notes, do NOT implement here ──
    # A ``Position`` model will add ``profile_id`` FK → ``activation_profiles.id``.
    # The relationship will be:
    #   positions: Mapped[List["Position"]] = relationship(
    #       back_populates="profile", cascade="all, delete-orphan",
    #       passive_deletes=True,
    #   )
    # so deleting a profile deletes its positions.
    # ``Position.profile_id`` is nullable=False but **updatable** — moving a
    # position between profiles = reassigning that FK.
    # Duplicating a profile deep-copies its positions (ProfileService._copy_positions).
