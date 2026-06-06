"""
Core Telegram bot handler – aiogram v3 dispatcher with all handlers.
"""

import logging
from datetime import date

from aiogram import Router
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.bot.keyboards.inline_kb import (
    DAY_NAMES,
    availability_kb,
    main_menu_kb,
    weekday_kb,
)
from app.config import settings

logger = logging.getLogger("ilutzim")
router = Router()


# ─── FSM States ────────────────────────────────────────────

class SubmissionFlow(StatesGroup):
    selecting_days = State()


class PhoneVerification(StatesGroup):
    waiting_for_phone = State()


# ─── Dependency helpers ────────────────────────────────────

async def _get_services():
    """Lazy-import services to avoid circular imports."""
    from app.services.user_service import UserService
    from app.services.submission_service import SubmissionService
    from app.services.week_service import WeekService
    from app.database import get_pool

    pool = get_pool()
    from app.repositories.user_repository import UserRepository
    user_repo = UserRepository(pool)
    user_svc = UserService(user_repo)
    week_svc = WeekService(pool)
    sub_svc = SubmissionService(pool)
    return user_svc, week_svc, sub_svc


# ─── /start ────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start – verify user, register if new, show main menu."""
    await state.clear()
    telegram_id = message.from_user.id
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""

    user_svc, _, _ = await _get_services()

    # Check if this Telegram ID is already linked to a user
    user = await user_svc.get_by_telegram_id(telegram_id)

    if user is not None:
        # Already registered — update profile info from Telegram
        try:
            await user_svc.update_user_profile(
                user.id,
                first_name=first_name,
                last_name=last_name,
                username=message.from_user.username or "",
            )
        except Exception:
            pass  # Non-critical — profile update failure shouldn't block
        await _show_main_menu(message, first_name)
    else:
        # Not yet linked — ask for phone number to verify identity
        await state.set_state(PhoneVerification.waiting_for_phone)
        await message.answer(
            "👋 שלום!\n\n"
            "כדי להשתמש במערכת, עליך לאמת את מספר הטלפון שלך.\n"
            "נא לשלוח את מספר הטלפון שאיתו נרשמת למערכת\n"
            "(ללא מקף, ללא רווחים).\n\n"
            "לדוגמה: 0501234567"
        )


# ─── Phone verification ────────────────────────────────────

@router.message(PhoneVerification.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Process phone number and link Telegram ID to user."""
    await state.clear()
    phone_raw = message.text.strip()

    # Normalize: remove spaces, dashes, and Hebrew prefix
    phone = phone_raw.replace("-", "").replace(" ", "")
    if phone.startswith("+972"):
        phone = "0" + phone[4:]
    elif phone.startswith("972"):
        phone = "0" + phone[3:]

    # Basic validation
    if not phone.isdigit() or len(phone) < 9:
        await message.answer(
            "❌ מספר הטלפון אינו תקין.\n"
            "נא לשלוח מספר טלפון בלבד (ללא מקף, ללא רווחים).\n\n"
            "לדוגמה: 0501234567"
        )
        await state.set_state(PhoneVerification.waiting_for_phone)
        return

    user_svc, _, _ = await _get_services()
    telegram_id = message.from_user.id

    # Find user by phone
    user = await user_svc.get_user_by_phone(phone)
    if user is None:
        logger.warning("Phone verification failed — phone not found: %s", phone)
        await message.answer(
            "❌ מספר הטלפון לא נמצא במערכת.\n"
            "נא לוודא שהמספר תואם למספר שנרשמת איתו.\n\n"
            "נסה שוב או פנה למנהל המערכת."
        )
        await state.set_state(PhoneVerification.waiting_for_phone)
        return

    if not user.is_active:
        await message.answer(
            "❌ המשתמש שלך אינו פעיל במערכת.\n"
            "פנה למנהל המערכת לפרטים."
        )
        return

    # Link telegram_id to the user
    try:
        await user_svc.link_telegram(phone, str(telegram_id))
        logger.info("Telegram linked: user_id=%s, telegram_id=%s", user.id, telegram_id)
    except Exception as exc:
        logger.error("Failed to link telegram: %s", exc)
        await message.answer(
            "❌ שגיאה בחיבור החשבון. נסה שוב מאוחר יותר."
        )
        return

    # Success — send welcome notification via the shared helper
    display_name = user.first_name or message.from_user.first_name or "שומר"
    try:
        from app.bot.notifications import notify_guard_welcome
        await notify_guard_welcome(
            telegram_id,
            user.first_name or "",
            user.last_name or "",
        )
    except Exception as notif_exc:
        logger.warning("Could not send welcome notification: %s", notif_exc)
        # Fallback — still show a success message in the chat
        await message.answer(
            f"✅ {display_name}, החשבון חובר בהצלחה!\n\n"
            f"מעתה תקבל הודעות ותזכורות דרך הבוט."
        )
    await _show_main_menu(message, display_name)


async def _show_main_menu(message: Message, display_name: str):
    """Show the main menu to an authenticated user."""
    telegram_id = message.from_user.id
    webapp_url = f"{settings.webapp_base_url}?tg_id={telegram_id}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 הגשת אילוצים", callback_data="submit")],
        [InlineKeyboardButton(text="📊 סטטוס אילוצים", callback_data="status")],
        [InlineKeyboardButton(
            text="🌐 כניסה למערכת",
            url=webapp_url,
        )],
        [InlineKeyboardButton(text="ℹ️ עזרה", callback_data="help")],
    ])
    await message.answer(
        f"שלום {display_name}! 👋\nברוך הבא למערכת ניהול האילוצים.",
        reply_markup=kb,
    )


# ─── Callback: main menu ───────────────────────────────────

@router.callback_query(lambda c: c.data == "menu")
async def cb_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "תפריט ראשי:",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()


# ─── Callback: submit constraints ──────────────────────────

@router.callback_query(lambda c: c.data == "submit")
async def cb_submit(callback: CallbackQuery, state: FSMContext):
    """Start submission flow – find current week."""
    _, week_svc, _ = await _get_services()
    telegram_id = callback.from_user.id

    week = await week_svc.get_active_week()
    if week is None:
        await callback.answer("אין שבוע פתוח להגשה כרגע.", show_alert=True)
        return

    await state.set_state(SubmissionFlow.selecting_days)
    await state.update_data(
        week_id=week["id"],
        availabilities={},  # day_index -> bool
    )

    start = week["week_start_date"]
    end = week["week_end_date"]
    await callback.message.edit_text(
        f"📅 הגשת אילוצים לשבוע:\n{start} – {end}\n\n"
        "בחר יום לסימון זמינות:",
        reply_markup=weekday_kb(str(week["id"])),
    )
    await callback.answer()


# ─── Callback: select a day ────────────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith("day:"))
async def cb_select_day(callback: CallbackQuery, state: FSMContext):
    """Show availability options for a specific day."""
    parts = callback.data.split(":")
    week_id = parts[1]
    day_index = int(parts[2])
    day_name = DAY_NAMES[day_index]

    data = await state.get_data()
    availabilities = data.get("availabilities", {})
    current = availabilities.get(str(day_index))

    status_text = ""
    if current is True:
        status_text = " (✅ זמין)"
    elif current is False:
        status_text = " (❌ לא זמין)"

    await callback.message.edit_text(
        f"📅 יום {day_name}{status_text}\nבחר זמינות:",
        reply_markup=availability_kb(week_id, day_index),
    )
    await callback.answer()


# ─── Callback: set availability ────────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith("avail:"))
async def cb_set_availability(callback: CallbackQuery, state: FSMContext):
    """Record availability for a day."""
    parts = callback.data.split(":")
    week_id = parts[1]
    day_index = parts[2]
    available = parts[3] == "yes"

    data = await state.get_data()
    availabilities = data.get("availabilities", {})
    availabilities[day_index] = available
    await state.update_data(availabilities=availabilities)

    day_name = DAY_NAMES[int(day_index)]
    status = "✅ זמין" if available else "❌ לא זמין"
    await callback.answer(f"יום {day_name}: {status}", show_alert=False)

    # Refresh the day view
    await callback.message.edit_text(
        f"📅 יום {day_name} ({status})\nבחר זמינות:",
        reply_markup=availability_kb(week_id, int(day_index)),
    )


# ─── Callback: back to days list ───────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith("backdays:"))
async def cb_back_to_days(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    week_id = parts[1]
    await callback.message.edit_text(
        "בחר יום לסימון זמינות:",
        reply_markup=weekday_kb(week_id),
    )
    await callback.answer()


# ─── Callback: finish submission ───────────────────────────

@router.callback_query(lambda c: c.data and c.data.startswith("finish:"))
async def cb_finish(callback: CallbackQuery, state: FSMContext):
    """Submit the week's availability."""
    data = await state.get_data()
    week_id = data.get("week_id")
    availabilities = data.get("availabilities", {})
    telegram_id = callback.from_user.id

    if not availabilities:
        await callback.answer("לא בחרת זמינות לאף יום!", show_alert=True)
        return

    await state.clear()

    user_svc, _, sub_svc = await _get_services()
    user = await user_svc.get_by_telegram_id(telegram_id)
    if user is None:
        await callback.answer("שגיאה: משתמש לא נמצא. שלח /start.", show_alert=True)
        return

    # Build availability records list
    availability_records = []
    for day_str, avail in availabilities.items():
        availability_records.append({
            "day_index": int(day_str),
            "is_available": avail,
        })

    try:
        await sub_svc.submit_weekly(
            user_id=user.id,
            week_id=week_id,
            availability_records=availability_records,
        )
    except Exception as exc:
        logger.error("Bot submission failed: %s", exc)
        await callback.message.edit_text(
            "❌ שגיאה בשמירת האילוצים. נסה שוב.",
            reply_markup=main_menu_kb(),
        )
        await callback.answer()
        return

    # Build summary
    lines = []
    for day_str, avail in sorted(availabilities.items(), key=lambda x: int(x[0])):
        name = DAY_NAMES[int(day_str)]
        status = "✅ זמין" if avail else "❌ לא זמין"
        lines.append(f"  {name}: {status}")

    await callback.message.edit_text(
        "✅ האילוצים נשמרו בהצלחה!\n\n" + "\n".join(lines),
        reply_markup=main_menu_kb(),
    )
    await callback.answer()


# ─── Callback: status ──────────────────────────────────────

@router.callback_query(lambda c: c.data == "status")
async def cb_status(callback: CallbackQuery):
    """Show submission status for the current week."""
    _, week_svc, sub_svc = await _get_services()
    telegram_id = callback.from_user.id

    week = await week_svc.get_active_week()
    if week is None:
        await callback.answer("אין שבוע פתוח כרגע.", show_alert=True)
        return

    user_svc, _, _ = await _get_services()
    user = await user_svc.get_by_telegram_id(telegram_id)
    if user is None:
        await callback.answer("משתמש לא רשום. שלח /start.", show_alert=True)
        return

    submission = await sub_svc.get_user_submission(user.id, week["id"])
    if submission is None:
        text = "📭 טרם הגשת אילוצים לשבוע הנוכחי."
    else:
        text = f"✅ הגשת אילוצים לשבוע {week['week_start_date']}.\nסטטוס: {submission.get('status', 'הוגש')}"

    await callback.message.edit_text(text, reply_markup=main_menu_kb())
    await callback.answer()


# ─── Callback: help ────────────────────────────────────────

@router.callback_query(lambda c: c.data == "help")
async def cb_help(callback: CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ <b>עזרה - מערכת ניהול אילוצים</b>\n\n"
        "📅 <b>הגשת אילוצים</b> — סמן את הימים שבהם אתה זמין/לא זמין\n"
        "📊 <b>סטטוס אילוצים</b> — בדוק אם הגשת אילוצים לשבוע הנוכחי\n"
        "🌐 <b>כניסה למערכת</b> — פתח את המערכת בדפדפן\n\n"
        "לתמיכה נוספת פנה למנהל המערכת.",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()


# ─── Fallback ──────────────────────────────────────────────

@router.message()
async def fallback(message: Message, state: FSMContext):
    """Catch-all for unrecognized messages."""
    # If user is in phone verification, redirect
    current_state = await state.get_state()
    if current_state == PhoneVerification.waiting_for_phone:
        await message.answer(
            "נא לשלוח מספר טלפון בלבד (ללא מקף, ללא רווחים).\n\n"
            "לדוגמה: 0501234567"
        )
        return
    await message.answer("לא הבנתי. השתמש בתפריט או שלח /start.")