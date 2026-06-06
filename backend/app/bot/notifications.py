"""
Proactive notification helpers for the Telegram bot.
"""

import logging
from datetime import date

from app.bot.bot_instance import get_bot

logger = logging.getLogger("ilutzim")


async def send_notification(telegram_id: int, text: str) -> bool:
    """Send a message to a single Telegram user."""
    try:
        bot = get_bot()
        await bot.send_message(chat_id=telegram_id, text=text)
        return True
    except Exception as exc:
        logger.error("Failed to send notification to %s: %s", telegram_id, exc)
        return False


async def broadcast_notifications(telegram_ids: list[int], text: str) -> int:
    """Send the same message to multiple users. Returns success count."""
    success = 0
    for tg_id in telegram_ids:
        if await send_notification(tg_id, text):
            success += 1
    return success


async def notify_week_opened(week_start: date, week_end: date, telegram_ids: list[int]):
    """Notify users that a new week is open for submissions."""
    text = (
        f"📢 <b>שבוע חדש נפתח!</b>\n\n"
        f"תאריכים: {week_start} – {week_end}\n"
        f"ניתן להגיש אילוצים דרך הבוט או המערכת.\n\n"
        f"שלח /start להתחלה."
    )
    count = await broadcast_notifications(telegram_ids, text)
    logger.info("Week-opened notification sent to %d/%d users", count, len(telegram_ids))
    return count


async def notify_guard_welcome(telegram_id: int, first_name: str, last_name: str) -> bool:
    """Send a welcome message to a newly added guard."""
    full_name = f"{first_name} {last_name}".strip()
    text = (
        f"👋 שלום {full_name}!\n\n"
        f"נרשמת בהצלחה למערכת ניהול האילוצים.\n"
        f"מעתה תקבל הודעות ותזכורות דרך הבוט הזה.\n\n"
        f"שלח /start לכניסה לתפריט הראשי."
    )
    return await send_notification(telegram_id, text)


async def notify_closing_reminder(week_start: date, deadline_text: str, telegram_ids: list[int]):
    """Remind users to submit before deadline."""
    text = (
        f"⏰ <b>תזכורת!</b>\n\n"
        f"שבוע {week_start} – ההגשה תיסגר {deadline_text}.\n"
        f"אם טרם הגשת, הגש עכשיו!\n\n"
        f"שלח /start להתחלה."
    )
    count = await broadcast_notifications(telegram_ids, text)
    logger.info("Closing reminder sent to %d/%d users", count, len(telegram_ids))
    return count