"""
Telegram bot package – aiogram v3 polling bot.
"""

from app.bot.bot_router import get_dispatcher, start_bot, stop_bot
from app.bot.bot_instance import get_bot
from app.bot.notifications import send_notification, broadcast_notifications
from app.bot.cron import setup_cron_jobs, scheduler

__all__ = [
    "get_dispatcher",
    "get_bot",
    "start_bot",
    "stop_bot",
    "send_notification",
    "broadcast_notifications",
    "setup_cron_jobs",
    "scheduler",
]