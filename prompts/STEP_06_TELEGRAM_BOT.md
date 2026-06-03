# Step 6 — Telegram Bot (aiogram v3) & Tests

## Context
You are continuing development of the Micro-SaaS security guard shift constraint management system. **Steps 0-5 (infrastructure, models, repositories, schemas, services, controllers) are complete. All previous tests pass.**

**Important:** All user-facing text is in Hebrew (centralized in `messages.py`). Code comments in English.

## Objective
Build the Telegram bot using aiogram v3 — authentication via contact sharing, WebApp keyboard integration, automated weekly notifications with smart skip, submission summary delivery, and cron-based scheduling. Write comprehensive tests.

## File Structure

```
app/bot/
├── __init__.py
├── bot_instance.py         # Bot + Dispatcher initialization
├── handlers/
│   ├── __init__.py
│   ├── start_handler.py    # /start command + contact sharing
│   ├── submit_handler.py   # /submit_anyway command
│   └── fallback_handler.py # Generic message handler
├── keyboards/
│   ├── __init__.py
│   ├── contact_keyboard.py # ReplyKeyboardMarkup for contact sharing
│   └── webapp_keyboard.py  # InlineKeyboardMarkup with WebApp button
├── middlewares/
│   ├── __init__.py
│   └── auth_middleware.py   # Check user exists and is_active
├── cron/
│   ├── __init__.py
│   └── weekly_opener.py    # Cron job for weekly notifications
└── notifications.py         # Send messages to users
```

## Detailed Requirements

### 1. `bot_instance.py`
- Initialize aiogram v3 `Bot` with token from `Settings`
- Initialize `Dispatcher`
- Register all handlers (routers)
- `async start_bot()` — start polling
- `async stop_bot()` — stop polling gracefully
- Integrate with FastAPI lifespan (start/stop bot alongside the web server)

### 2. `start_handler.py` — Authentication Flow
- **`/start` command:**
  - Send `Messages.BOT_WELCOME` with `contact_keyboard` (ReplyKeyboardMarkup)
  - The welcome message explains the guard needs to share their phone contact
  
- **Contact received (ContentType.CONTACT):**
  - Extract `phone_number` from contact
  - Normalize: strip "+972" prefix → "05...", remove spaces/dashes
  - Look up in DB via `UserService.link_telegram(phone, telegram_id)`
  - If found: send `Messages.BOT_AUTH_SUCCESS` + `webapp_keyboard`
  - If not found: send `Messages.BOT_AUTH_FAIL`
  - Log the result (success/failure + phone)

### 3. `submit_handler.py` — `/submit_anyway`
- Check if user is authenticated (has telegram_id in DB)
- If authenticated: send `Messages.BOT_SUBMIT_ANYWAY` + `webapp_keyboard` (inline)
- If not authenticated: send `Messages.BOT_AUTH_FAIL`

### 4. `fallback_handler.py`
- Catch-all for any unrecognized message
- Check if current week is locked/published via `WeekService`
- If locked: send `Messages.BOT_LOCKOUT`
- If open: send a default message with `webapp_keyboard`

### 5. `contact_keyboard.py`
```python
def get_contact_keyboard() -> ReplyKeyboardMarkup:
    # Single button: Messages.BOT_SHARE_CONTACT_BUTTON
    # request_contact=True
    # one_time_keyboard=True
    # resize_keyboard=True
```

### 6. `webapp_keyboard.py`
```python
def get_webapp_keyboard() -> InlineKeyboardMarkup:
    # Single InlineKeyboardButton with:
    #   text = Messages.BOT_OPEN_WEBAPP_BUTTON
    #   web_app = WebAppInfo(url=settings.WEBAPP_URL)
```

### 7. `auth_middleware.py`
aiogram middleware that runs before handlers:
- Extract `telegram_id` from update
- Look up user in DB
- If not found or not active → skip handler, optionally log
- If found → inject user into handler data (`data["user"] = user`)

### 8. `weekly_opener.py` — Cron Job
```python
async def run_weekly_opening():
    """
    Scheduled weekly task (day and hour from Settings).
    
    1. Get current open week (via WeekService)
    2. If no open week → log warning, return
    3. Get all active users (via UserService)
    4. For each user:
       a. Check is_user_fully_absent() via EventService (smart skip)
       b. If fully absent → log "Auto-Absence: {user.full_name}", skip
       c. If not absent → send BOT_WEEK_OPEN + webapp_keyboard
       d. Handle TelegramBadRequest (bot blocked) → log warning, skip
    5. Return stats: {sent: N, skipped_absent: N, failed: N}
    """
```

Schedule registration:
- Use `apscheduler` AsyncIOScheduler or `asyncio` periodic task
- Read schedule from `Settings.CRON_WEEKLY_OPEN_DAY` and `Settings.CRON_WEEKLY_OPEN_HOUR`
- Register in bot startup

### 9. `notifications.py` — Message Sending Functions
```python
async def send_submission_summary(bot: Bot, telegram_id: str, summary_text: str) -> bool:
    """Send submission summary. Returns True on success, False on failure."""

async def send_deviation_warning(bot: Bot, telegram_id: str, warning_text: str) -> bool:
    """Send deviation warning. Returns True on success, False on failure."""

async def send_reminder(bot: Bot, telegram_id: str) -> bool:
    """Send Messages.BOT_REMINDER + webapp_keyboard. Returns True/False."""

async def send_weekly_opening(bot: Bot, telegram_id: str) -> bool:
    """Send Messages.BOT_WEEK_OPEN + webapp_keyboard. Returns True/False."""
```

All functions:
- Wrap in try/except
- Catch `TelegramBadRequest` (user blocked bot) → log warning, return False
- Catch generic exceptions → log error, return False
- Log success → return True

### 10. Integration Updates

**Update `app/main.py`:**
- Add bot startup/shutdown to lifespan context manager
- Start cron scheduler

**Update `app/services/submission_service.py`:**
- After successful submission in `submit_constraints()`:
  - Build summary via `NotificationService.build_submission_summary()`
  - If has_deviation: build warning via `NotificationService.build_deviation_warning()`
  - Send summary + optional warning via `notifications.send_submission_summary()` / `send_deviation_warning()`
  - If sending fails → log warning (don't fail the submission)

**Update `app/controllers/admin_notifications_controller.py`:**
- Implement the real `send-reminder` endpoint:
  - Get missing users via `SubmissionService.get_missing_users()`
  - For each: call `notifications.send_reminder()`
  - Return count of sent/failed

## Tests Required

### `tests/test_bot.py` (8 tests)
Use aiogram's test utilities or mock the Bot object.

1. `test_start_handler_sends_welcome` — `/start` → sends Messages.BOT_WELCOME + contact keyboard
2. `test_contact_handler_valid_phone` — Share contact with known phone → auth success + telegram_id saved
3. `test_contact_handler_invalid_phone` — Share contact with unknown phone → auth fail message
4. `test_contact_handler_normalizes_phone` — Phone "+972501234567" normalized to "0501234567" before lookup
5. `test_submit_anyway_authenticated` — Authenticated user → webapp keyboard sent
6. `test_submit_anyway_unauthenticated` — Non-authenticated user → auth fail
7. `test_fallback_locked_week` — Message during locked week → lockout message
8. `test_auth_middleware_blocks_inactive` — Middleware skips handler for inactive user

### `tests/test_cron.py` (5 tests)
9. `test_weekly_opener_sends_to_active` — Active users with no events receive opening message
10. `test_weekly_opener_skips_fully_absent` — User with full-week military reserve → skipped (auto-absence)
11. `test_weekly_opener_handles_blocked_bot` — TelegramBadRequest → logged, counted as failed
12. `test_weekly_opener_no_open_week` — No open week exists → log warning, zero messages sent
13. `test_weekly_opener_returns_stats` — Correct sent/skipped/failed counts returned

### `tests/test_notifications.py` (4 tests)
14. `test_send_submission_summary_success` — Mock bot → message sent → returns True
15. `test_send_submission_summary_with_deviation` — Summary + deviation warning both sent
16. `test_send_reminder_success` — Reminder sent → returns True
17. `test_send_reminder_bot_blocked` — TelegramBadRequest → returns False, logged

## Rules
- ALL text from `messages.py` — zero hard-coded Hebrew in bot code
- Error handling: if a user blocked the bot → log + skip (never crash)
- Detailed logging at every step (who received, who was skipped, what failed)
- Async/await everywhere
- Bot token from config (never hard-coded)
- Tests use mocked Bot (no real Telegram API calls)
- All tests must pass with `pytest`
- Code comments in English
