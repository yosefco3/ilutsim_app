# Test Coverage Graph

_נוצר אוטומטית ב: 2026-06-12 18:24_
**טרנד:**  →0%

## סיכום

| מדד | ערך |
|---|---|
| קבצי קוד backend | 57 |
| קבצי קוד מכוסים בטסטים | 37 |
| קבצי קוד ללא טסטים | 20 |
| אחוז כיסוי | 64% →0% |
| טסטים עוברים (backend) | 18 ✅ |
| טסטים נכשלים (backend) | 0 ❌ |
| קבצי קוד frontend (ממופים) | 10 |
| טסטים עוברים (frontend) | 15 ✅ |
| טסטים נכשלים (frontend) | 0 ❌ |

## Backend: מיפוי קוד → טסטים

| קובץ קוד | קובץ טסט | סטטוס |
|---|---|---|
| `bot/bot_router.py` | `test_bot.py` | 🟢 PASS |
| `bot/core.py` | `test_bot.py` | 🟢 PASS |
| `bot/cron.py` | `test_bot.py` | 🟢 PASS |
| `bot/notifications.py` | `test_bot.py` | 🟢 PASS |
| `bot/notifications.py` | `test_notification_on_open.py` | 🟢 PASS |
| `config.py` | `test_config.py` | 🟢 PASS |
| `constants.py` | `test_status_transitions.py` | 🟢 PASS |
| `controllers/admin_events_controller.py` | `test_controllers.py` | 🟢 PASS |
| `controllers/admin_export_controller.py` | `test_controllers.py` | 🟢 PASS |
| `controllers/admin_export_controller.py` | `test_export.py` | 🟢 PASS |
| `controllers/admin_notifications_controller.py` | `test_controllers.py` | 🟢 PASS |
| `controllers/admin_users_controller.py` | `test_controllers.py` | 🟢 PASS |
| `controllers/admin_weeks_controller.py` | `test_controllers.py` | 🟢 PASS |
| `controllers/admin_weeks_controller.py` | `test_open_week.py` | 🟢 PASS |
| `controllers/auth_controller.py` | `test_controllers.py` | 🟢 PASS |
| `controllers/submission_controller.py` | `test_controllers.py` | 🟢 PASS |
| `controllers/submission_controller.py` | `test_submission_guard.py` | 🟢 PASS |
| `main.py` | `test_e2e.py` | ⚪ ⚠️ NOT RUN |
| `main.py` | `test_health.py` | 🟢 PASS |
| `models/admin.py` | `test_models.py` | 🟢 PASS |
| `models/daily_status.py` | `test_models.py` | 🟢 PASS |
| `models/schedule_event.py` | `test_models.py` | 🟢 PASS |
| `models/schedule_week.py` | `test_models.py` | 🟢 PASS |
| `models/shift_window.py` | `test_models.py` | 🟢 PASS |
| `models/system_setting.py` | `test_models.py` | 🟢 PASS |
| `models/user.py` | `test_models.py` | 🟢 PASS |
| `models/weekly_submission.py` | `test_models.py` | 🟢 PASS |
| `repositories/admin_repository.py` | `test_repositories.py` | 🟢 PASS |
| `repositories/schedule_event_repository.py` | `test_repositories.py` | 🟢 PASS |
| `repositories/schedule_week_repository.py` | `test_current_week.py` | 🟢 PASS |
| `repositories/schedule_week_repository.py` | `test_repositories.py` | 🟢 PASS |
| `repositories/schedule_week_repository.py` | `test_week_workflow.py` | 🟢 PASS |
| `repositories/submission_repository.py` | `test_repositories.py` | 🟢 PASS |
| `repositories/system_settings_repository.py` | `test_repositories.py` | 🟢 PASS |
| `repositories/user_repository.py` | `test_repositories.py` | 🟢 PASS |
| `schemas/common_schemas.py` | `test_schemas.py` | 🟢 PASS |
| `schemas/event_schemas.py` | `test_schemas.py` | 🟢 PASS |
| `schemas/submission_schemas.py` | `test_schemas.py` | 🟢 PASS |
| `schemas/user_schemas.py` | `test_schemas.py` | 🟢 PASS |
| `schemas/week_schemas.py` | `test_schemas.py` | 🟢 PASS |
| `seed.py` | `test_initial_seed.py` | 🟢 PASS |
| `services/excel_export_service.py` | `test_export.py` | 🟢 PASS |
| `services/week_service.py` | `test_current_week.py` | 🟢 PASS |
| `services/week_service.py` | `test_notification_on_open.py` | 🟢 PASS |
| `services/week_service.py` | `test_open_week.py` | 🟢 PASS |
| `services/week_service.py` | `test_status_transitions.py` | 🟢 PASS |
| `services/week_service.py` | `test_submission_guard.py` | 🟢 PASS |
| `services/week_service.py` | `test_week_workflow.py` | 🟢 PASS |
| `utils/date_utils.py` | `test_date_utils.py` | 🟢 PASS |

## Backend: קבצים ללא טסטים (מדורגים לפי חשיבות)

| עדיפות | קובץ קוד | תיקייה |
|---|---|---|
| 🔴 HIGH | `admin_admins_controller.py` | `app/controllers` |
| 🔴 HIGH | `admin_settings_controller.py` | `app/controllers` |
| 🔴 HIGH | `base_repository.py` | `app/repositories` |
| 🔴 HIGH | `admin_service.py` | `app/services` |
| 🔴 HIGH | `auth_service.py` | `app/services` |
| 🔴 HIGH | `deviation_service.py` | `app/services` |
| 🔴 HIGH | `event_service.py` | `app/services` |
| 🔴 HIGH | `settings_service.py` | `app/services` |
| 🔴 HIGH | `submission_service.py` | `app/services` |
| 🔴 HIGH | `user_service.py` | `app/services` |
| 🟡 MEDIUM | `inline_kb.py` | `app/bot/keyboards` |
| 🟡 MEDIUM | `auth.py` | `app/bot/middlewares` |
| 🟡 MEDIUM | `telegram_auth.py` | `app/utils` |
| ⚪ LOW | `bot_instance.py` | `app/bot` |
| ⚪ LOW | `database.py` | `app` |
| ⚪ LOW | `dependencies.py` | `app` |
| ⚪ LOW | `exceptions.py` | `app` |
| ⚪ LOW | `logging_config.py` | `app` |
| ⚪ LOW | `messages.py` | `app` |
| ⚪ LOW | `base.py` | `app/models` |

## Frontend: מיפוי טסטים

| תת-פרויקט | קובץ קוד | קובץ טסט | סטטוס |
|---|---|---|---|
| admin | `src/api/adminApiClient.js` | `tests/apiClient.test.js` | 🟢 PASS |
| admin | `src/components/EventForm.jsx` | `tests/components.test.jsx` | 🟢 PASS |
| admin | `src/components/ProtectedRoute.jsx` | `tests/components.test.jsx` | 🟢 PASS |
| admin | `src/components/StatusGrid.jsx` | `tests/components.test.jsx` | 🟢 PASS |
| admin | `src/components/Navbar.jsx` | `tests/components.test.jsx` | 🟢 PASS |
| admin | `src/components/WeekStatusControl.jsx` | `tests/components.test.jsx` | 🟢 PASS |
| admin | `src/components/ConfirmDialog.jsx` | `tests/components.test.jsx` | 🟢 PASS |
| admin | `src/components/GuardForm.jsx` | `tests/components.test.jsx` | 🟢 PASS |
| admin | `src/components/GuardTable.jsx` | `tests/components.test.jsx` | 🟢 PASS |
| admin | `src/utils/messages.js` | `tests/messages.test.js` | 🟢 PASS |

## Backend: רשימת קבצי טסט

| קובץ טסט | מכסה קבצי קוד | סטטוס |
|---|---|---|
| `test_bot.py` | 4 | 🟢 |
| `test_config.py` | 1 | 🟢 |
| `test_controllers.py` | 7 | 🟢 |
| `test_current_week.py` | 2 | 🟢 |
| `test_date_utils.py` | 1 | 🟢 |
| `test_e2e.py` | 1 | ⚪ |
| `test_export.py` | 2 | 🟢 |
| `test_health.py` | 1 | 🟢 |
| `test_initial_seed.py` | 1 | 🟢 |
| `test_models.py` | 8 | 🟢 |
| `test_notification_on_open.py` | 2 | 🟢 |
| `test_open_week.py` | 2 | 🟢 |
| `test_repositories.py` | 6 | 🟢 |
| `test_schemas.py` | 5 | 🟢 |
| `test_status_transitions.py` | 2 | 🟢 |
| `test_submission_guard.py` | 2 | 🟢 |
| `test_submission_notification.py` | 1 | 🟢 |
| `test_submission_persistence.py` | 1 | 🟢 |
| `test_week_workflow.py` | 2 | 🟢 |
