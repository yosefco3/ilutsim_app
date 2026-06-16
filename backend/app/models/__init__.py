"""
Models package — import all models so Alembic autogenerate detects them.
"""

from app.models.base import Base, BaseModel
from app.models.user import User
from app.models.schedule_week import ScheduleWeek
from app.models.weekly_submission import WeeklySubmission
from app.models.daily_status import DailyStatus
from app.models.shift_window import ShiftWindow
from app.models.admin import Admin
from app.models.system_setting import SystemSetting

# Part B (schedule builder) models — imported here ONLY so Alembic autogenerate
# sees them in Base.metadata. The code itself lives under app/schedule_builder/.
from app.schedule_builder.models.activation_profile import ActivationProfile  # noqa: E402,F401
from app.schedule_builder.models.position import Position  # noqa: E402,F401

__all__ = [
    "Base",
    "BaseModel",
    "User",
    "ScheduleWeek",
    "WeeklySubmission",
    "DailyStatus",
    "ShiftWindow",
    "Admin",
    "SystemSetting",
]
