"""
Proactive notification helpers for the Telegram bot.
"""

import logging
from datetime import date

from app.bot.bot_instance import get_bot

logger = logging.getLogger("ilutzim")


async def send_notification(telegram_id: int, text: str, reply_markup=None) -> bool:
    """Send a message to a single Telegram user."""
    try:
        bot = get_bot()
        if bot is None:
            logger.error("send_notification: bot is None — cannot send to telegram_id=%s", telegram_id)
            return False
        logger.info("send_notification: sending to telegram_id=%s (text length=%d)", telegram_id, len(text))
        await bot.send_message(chat_id=telegram_id, text=text, reply_markup=reply_markup)
        logger.info("send_notification: SUCCESS for telegram_id=%s", telegram_id)
        return True
    except Exception as exc:
        logger.error("send_notification: FAILED for telegram_id=%s — %s", telegram_id, exc, exc_info=True)
        return False


async def broadcast_notifications(telegram_ids: list[int], text: str, reply_markup=None) -> int:
    """Send the same message to multiple users. Returns success count."""
    success = 0
    for tg_id in telegram_ids:
        if await send_notification(tg_id, text, reply_markup=reply_markup):
            success += 1
    return success


async def notify_week_opened(week_start: date, week_end: date, telegram_ids: list[int]):
    """Notify users that a new week is open for submissions.

    Uses DD/MM/YYYY date format and includes the webapp URL.
    Returns count of successfully notified guards.
    """
    from app.bot.keyboards.inline_kb import submit_constraints_kb

    start_fmt = week_start.strftime("%d/%m/%Y")
    end_fmt = week_end.strftime("%d/%m/%Y")

    text = (
        "🔔 שבוע חדש נפתח להגשה!\n\n"
        f"תאריכים: {start_fmt} - {end_fmt}"
    )
    count = await broadcast_notifications(
        telegram_ids, text, reply_markup=submit_constraints_kb()
    )
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
    """Notify users that a week was finalized (LOCKED) — no more edits.

    This is the broadcast for a *manual* finalize (the admin "publish" action).
    The Sunday rollover also locks weeks but does so silently (notify=False).
    """
    start_fmt = week_start.strftime("%d/%m/%Y")
    end_fmt = week_end.strftime("%d/%m/%Y")
    text = f"🔒 שבוע {start_fmt} - {end_fmt} ננעל — לא ניתן עוד לעדכן אילוצים"
    count = await broadcast_notifications(telegram_ids, text)
    logger.info("Week-locked notification sent to %d/%d users", count, len(telegram_ids))
    return count


async def notify_closing_reminder(
    week_start: date,
    deadline_text: str,
    recipients: list[dict],
    week_end: date | None = None,
):
    """Remind guards who haven't submitted yet to submit before the deadline.

    ``recipients`` is a list of ``{"telegram_id": int, "name": str}`` dicts so the
    message can greet each registered guard by name. The message includes a WebApp
    button to submit directly — registered guards never need to send ``/start``.
    Returns count of successfully notified guards.
    """
    from app.bot.keyboards.inline_kb import submit_constraints_kb

    start_fmt = week_start.strftime("%d/%m/%Y")
    week_range = start_fmt
    if week_end is not None:
        week_range = f"{start_fmt} - {week_end.strftime('%d/%m/%Y')}"

    keyboard = submit_constraints_kb()
    count = 0
    for recipient in recipients:
        name = (recipient.get("name") or "").strip()
        greeting = f"שלום {name}! 👋\n\n" if name else ""
        text = (
            f"⏰ <b>תזכורת!</b>\n\n"
            f"{greeting}"
            f"טרם הגשת את האילוצים לשבוע {week_range}.\n"
            f"ההגשה תיסגר {deadline_text}.\n\n"
            f"אנא הגש עכשיו דרך הכפתור למטה 👇"
        )
        if await send_notification(recipient["telegram_id"], text, reply_markup=keyboard):
            count += 1
    logger.info("Closing reminder sent to %d/%d users", count, len(recipients))
    return count


async def notify_admin_filled_constraints(telegram_id: int, week_label: str) -> bool:
    """Notify a guard that an admin filled their constraints on their behalf."""
    from app.bot.keyboards.inline_kb import submission_success_kb

    text = (
        "📝 האדמין מילא עבורך את האילוצים\n\n"
        f"שבוע: {week_label}\n\n"
        "ניתן לצפות ולערוך את האילוצים כל עוד השבוע פתוח."
    )
    try:
        bot = get_bot()
        if bot is None:
            logger.error("notify_admin_filled_constraints: bot is None")
            return False
        await bot.send_message(
            chat_id=telegram_id,
            text=text,
            reply_markup=submission_success_kb(),
        )
        logger.info("Admin-filled-constraints notification sent to telegram_id=%s", telegram_id)
        return True
    except Exception as exc:
        logger.error("notify_admin_filled_constraints: FAILED for telegram_id=%s — %s", telegram_id, exc)
        return False


async def notify_submission_success(telegram_id: int, week_label: str) -> bool:
    """Notify a guard that their submission was received successfully."""
    from app.bot.keyboards.inline_kb import submission_success_kb

    text = (
        "✅ האילוצים נשלחו בהצלחה!\n\n"
        f"שבוע: {week_label}\n\n"
        "ניתן לערוך את האילוצים כל עוד השבוע פתוח."
    )
    try:
        bot = get_bot()
        if bot is None:
            logger.error("notify_submission_success: bot is None")
            return False
        await bot.send_message(
            chat_id=telegram_id,
            text=text,
            reply_markup=submission_success_kb(),
        )
        logger.info("Submission success notification sent to telegram_id=%s", telegram_id)
        return True
    except Exception as exc:
        logger.error("notify_submission_success: FAILED for telegram_id=%s — %s", telegram_id, exc)
        return False
