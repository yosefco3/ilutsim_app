"""
Bot instance singleton for aiogram v3.
"""

import logging

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from app.config import get_settings

logger = logging.getLogger("ilutzim")

_bot: Bot | None = None


def get_bot() -> Bot:
    """Return the singleton Bot instance."""
    global _bot
    if _bot is None:
        settings = get_settings()
        if not settings.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is not configured")
        _bot = Bot(
            token=settings.TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode="HTML"),
        )
        logger.info("Telegram Bot instance created")
    return _bot


async def rebuild_bot(token: str) -> Bot:
    """Close the existing Bot (if any) and create a new one with ``token``.

    Used to apply a new bot token live without restarting the server.
    """
    global _bot
    if _bot is not None:
        try:
            await _bot.session.close()
        except Exception:  # pragma: no cover - best-effort cleanup
            logger.warning("Failed closing old bot session", exc_info=True)
    _bot = Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))
    logger.info("Telegram Bot instance rebuilt")
    return _bot