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
    """Weekly schedule lifecycle status."""
    OPEN = "open"
    LOCKED = "locked"
    PUBLISHED = "published"


class EventType(str, enum.Enum):
    """Event types that affect guard availability."""
    VACATION = "vacation"
    MILITARY_RESERVE = "military_reserve"
    FIREARMS_TRAINING = "firearms_training"


class SubmissionStatus(str, enum.Enum):
    """Status of a guard's weekly submission."""
    SUBMITTED = "submitted"
    SUBMITTED_WITH_VARIANCE = "submitted_with_variance"
    PENDING = "pending"
    AUTO_ABSENCE = "auto_absence"


class UserRole(str, enum.Enum):
    """Guard roles within the system."""
    GUARD = "guard"
    SHIFT_LEAD = "shift_lead"
    SCANNER = "scanner"


class AdminRole(str, enum.Enum):
    """Admin roles with hierarchical permissions.

    - super_admin: full access to everything
    - admin: manage guards, weeks, events
    - viewer: read-only access
    """
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    VIEWER = "viewer"