"""
Bot instance singleton for aiogram v3.
"""

import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from app.config import settings

logger = logging.getLogger("ilutzim")

_bot: Bot | None = None


def get_bot() -> Bot:
    """Return the singleton Bot instance."""
    global _bot
    if _bot is None:
        _bot = Bot(
            token=settings.telegram_bot_token,
            default=DefaultBotProperties(parse_mode="HTML"),
        )
        logger.info("Telegram Bot instance created")
    return _bot