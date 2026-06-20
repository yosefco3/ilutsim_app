"""
Enums and default values for the application.
"""

import enum


class ShiftType(str, enum.Enum):
    """Shift types throughout the day."""
    MORNING = "morning"
    AFTERNOON = "afternoon"
    NIGHT = "night"


class WeekStatus(str, enum.Enum):
    """Weekly schedule lifecycle status (3-state model).

    CLOSED  — submissions closed but reopenable; admin may edit on behalf of guards.
    OPEN    — submissions accepted.
    LOCKED  — final, non-reopenable. Reached by the Sunday rollover or by the admin
              "publish" action (which merged into LOCKED — there is no PUBLISHED).
    """
    CLOSED = "closed"
    OPEN = "open"
    LOCKED = "locked"


class SubmissionStatus(str, enum.Enum):
    """Status of a guard's weekly submission."""
    SUBMITTED = "submitted"
    SUBMITTED_WITH_VARIANCE = "submitted_with_variance"
    PENDING = "pending"
    AUTO_ABSENCE = "auto_absence"


class UserRole(str, enum.Enum):
    """Guard roles within the system."""
    AHMASH = "AHMASH"
    BASIC_GUARD = "BASIC_GUARD"
    LEVEL_B = "LEVEL_B"
    NINE_HOURS = "NINE_HOURS"
    UNARMED = "UNARMED"
    CHECKER = "CHECKER"


class AdminRole(str, enum.Enum):
    """Admin roles with hierarchical permissions.

    - super_admin: full access to everything
    - admin: manage guards, weeks
    - viewer: read-only access
    """
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    VIEWER = "viewer"