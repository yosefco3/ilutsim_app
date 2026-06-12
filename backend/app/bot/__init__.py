"""
Telegram bot package – aiogram v3 polling bot.
"""

from app.bot.bot_router import (
    get_dispatcher,
    start_bot,
    stop_bot,
    restart_bot_with_token,
)
from app.bot.bot_instance import get_bot
from app.bot.notifications import send_notification, broadcast_notifications

__all__ = [
    "get_dispatcher",
    "get_bot",
    "start_bot",
    "stop_bot",
    "restart_bot_with_token",
    "send_notification",
    "broadcast_notifications",
]
