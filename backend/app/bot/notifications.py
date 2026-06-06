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
        if bot is None:
            logger.error("send_notification: bot is None — cannot send to telegram_id=%s", telegram_id)
            return False
        logger.info("send_notification: sending to telegram_id=%s (text length=%d)", telegram_id, len(text))
        await bot.send_message(chat_id=telegram_id, text=text)
        logger.info("send_notification: SUCCESS for telegram_id=%s", telegram_id)
        return True
    except Exception as exc:
        logger.error("send_notification: FAILED for telegram_id=%s — %s", telegram_id, exc, exc_info=True)
        return False


async def broadcast_notifications(telegram_ids: list[int], text: str) -> int:
    """Send the same message to multiple users. Returns success count."""
    success = 0
    for tg_id in telegram_ids:
        if await send_notification(tg_id, text):
            success += 1
    return success


async def notify_week_opened(week_start: date, week_end: date, telegram_ids: list[int]):
    """Notify users that a new week is open for submissions.

    Uses DD/MM/YYYY date format and includes the webapp URL.
    Returns count of successfully notified guards.
    """
    from app.config import settings

    start_fmt = week_start.strftime("%d/%m/%Y")
    end_fmt = week_end.strftime("%d/%m/%Y")

    text = (
        "🔔 שבוע חדש נפתח להגשה!\n\n"
        f"תאריכים: {start_fmt} - {end_fmt}\n\n"
        "לחץ כאן למילוי אילוצים:\n"
        f"{settings.WEBAPP_URL}"
    )
    count = await broadcast_notifications(telegram_ids, text)
    logger.info("Week-opened notification sent to %d/%d users", count, len(telegram_ids))
    return count


async def notify_guard_welcome(telegram_id: int, first_name: str, last_name: str) -> bool:
    """Send a welcome message to a newly added guard."""
    full_name = f"{first_name} {last_name}".strip()
    logger.info(
        "notify_guard_welcome: telegram_id=%s, name=%s",
        telegram_id, full_name,
    )
    text = (
        f"👋 שלום {full_name}!\n\n"
        f"נרשמת בהצלחה למערכת ניהול האילוצים.\n"
        f"מעתה תקבל הודעות ותזכורות דרך הבוט הזה."
    )
    return await send_notification(telegram_id, text)


async def notify_week_locked(week_start: date, week_end: date, telegram_ids: list[int]):
    """Notify users that a week was locked for submissions."""
    start_fmt = week_start.strftime("%d/%m/%Y")
    end_fmt = week_end.strftime("%d/%m/%Y")
    text = f"🔒 שבוע {start_fmt} - {end_fmt} נסגר להגשות"
    count = await broadcast_notifications(telegram_ids, text)
    logger.info("Week-locked notification sent to %d/%d users", count, len(telegram_ids))
    return count


async def notify_week_published(week_start: date, week_end: date, telegram_ids: list[int]):
    """Notify users that a week's schedule was published."""
    start_fmt = week_start.strftime("%d/%m/%Y")
    end_fmt = week_end.strftime("%d/%m/%Y")
    text = f"✅ סידור העבודה לשבוע {start_fmt} - {end_fmt} פורסם!"
    count = await broadcast_notifications(telegram_ids, text)
    logger.info("Week-published notification sent to %d/%d users", count, len(telegram_ids))
    return count


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