"""
Models package — import all models so Alembic autogenerate detects them.
"""

from app.models.base import Base, BaseModel
from app.models.user import User
from app.models.schedule_week import ScheduleWeek
from app.models.schedule_event import ScheduleEvent
from app.models.weekly_submission import WeeklySubmission
from app.models.daily_status import DailyStatus
from app.models.shift_window import ShiftWindow
from app.models.admin import Admin
from app.models.system_setting import SystemSetting

__all__ = [
    "Base",
    "BaseModel",
    "User",
    "ScheduleWeek",
    "ScheduleEvent",
    "WeeklySubmission",
    "DailyStatus",
    "ShiftWindow",
    "Admin",
    "SystemSetting",
]
