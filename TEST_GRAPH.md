# Test Coverage Graph

_נוצר אוטומטית ב: 2026-06-06 20:02_

## סיכום

| מדד | ערך |
|---|---|
| קבצי קוד backend | 57 |
| קבצי קוד מכוסים בטסטים | 37 |
| קבצי קוד ללא טסטים | 20 |
| אחוז כיסוי | 64% |
| טסטים עוברים (backend) | 0 ✅ |
| טסטים נכשלים (backend) | 3 ❌ |

## Backend: מיפוי קוד → טסטים

| קובץ קוד | קובץ טסט | סטטוס |
|---|---|---|
| `bot/bot_router.py` | `test_bot.py` | ⚪ ⚠️ NOT RUN |
| `bot/core.py` | `test_bot.py` | ⚪ ⚠️ NOT RUN |
| `bot/cron.py` | `test_bot.py` | ⚪ ⚠️ NOT RUN |
| `bot/notifications.py` | `test_bot.py` | ⚪ ⚠️ NOT RUN |
| `bot/notifications.py` | `test_notification_on_open.py` | ⚪ ⚠️ NOT RUN |
| `config.py` | `test_config.py` | ⚪ ⚠️ NOT RUN |
| `constants.py` | `test_status_transitions.py` | ⚪ ⚠️ NOT RUN |
| `controllers/admin_events_controller.py` | `test_controllers.py` | ⚪ ⚠️ NOT RUN |
| `controllers/admin_export_controller.py` | `test_controllers.py` | ⚪ ⚠️ NOT RUN |
| `controllers/admin_export_controller.py` | `test_export.py` | ⚪ ⚠️ NOT RUN |
| `controllers/admin_notifications_controller.py` | `test_controllers.py` | ⚪ ⚠️ NOT RUN |
| `controllers/admin_users_controller.py` | `test_controllers.py` | ⚪ ⚠️ NOT RUN |
| `controllers/admin_weeks_controller.py` | `test_controllers.py` | ⚪ ⚠️ NOT RUN |
| `controllers/admin_weeks_controller.py` | `test_open_week.py` | ⚪ ⚠️ NOT RUN |
| `controllers/auth_controller.py` | `test_controllers.py` | ⚪ ⚠️ NOT RUN |
| `controllers/submission_controller.py` | `test_controllers.py` | ⚪ ⚠️ NOT RUN |
| `controllers/submission_controller.py` | `test_submission_guard.py` | ⚪ ⚠️ NOT RUN |
| `main.py` | `test_e2e.py` | ⚪ ⚠️ NOT RUN |
| `main.py` | `test_health.py` | ⚪ ⚠️ NOT RUN |
| `models/admin.py` | `test_models.py` | 🔴 FAIL |
| `models/daily_status.py` | `test_models.py` | 🔴 FAIL |
| `models/schedule_event.py` | `test_models.py` | 🔴 FAIL |
| `models/schedule_week.py` | `test_models.py` | 🔴 FAIL |
| `models/shift_window.py` | `test_models.py` | 🔴 FAIL |
| `models/system_setting.py` | `test_models.py` | 🔴 FAIL |
| `models/user.py` | `test_models.py` | 🔴 FAIL |
| `models/weekly_submission.py` | `test_models.py` | 🔴 FAIL |
| `repositories/admin_repository.py` | `test_repositories.py` | 🔴 FAIL |
| `repositories/schedule_event_repository.py` | `test_repositories.py` | 🔴 FAIL |
| `repositories/schedule_week_repository.py` | `test_current_week.py` | ⚪ ⚠️ NOT RUN |
| `repositories/schedule_week_repository.py` | `test_repositories.py` | 🔴 FAIL |
| `repositories/schedule_week_repository.py` | `test_week_workflow.py` | ⚪ ⚠️ NOT RUN |
| `repositories/submission_repository.py` | `test_repositories.py` | 🔴 FAIL |
| `repositories/system_settings_repository.py` | `test_repositories.py` | 🔴 FAIL |
| `repositories/user_repository.py` | `test_repositories.py` | 🔴 FAIL |
| `schemas/common_schemas.py` | `test_schemas.py` | 🔴 FAIL |
| `schemas/event_schemas.py` | `test_schemas.py` | 🔴 FAIL |
| `schemas/submission_schemas.py` | `test_schemas.py` | 🔴 FAIL |
| `schemas/user_schemas.py` | `test_schemas.py` | 🔴 FAIL |
| `schemas/week_schemas.py` | `test_schemas.py` | 🔴 FAIL |
| `seed.py` | `test_initial_seed.py` | ⚪ ⚠️ NOT RUN |
| `services/excel_export_service.py` | `test_export.py` | ⚪ ⚠️ NOT RUN |
| `services/week_service.py` | `test_current_week.py` | ⚪ ⚠️ NOT RUN |
| `services/week_service.py` | `test_notification_on_open.py` | ⚪ ⚠️ NOT RUN |
| `services/week_service.py` | `test_open_week.py` | ⚪ ⚠️ NOT RUN |
| `services/week_service.py` | `test_status_transitions.py` | ⚪ ⚠️ NOT RUN |
| `services/week_service.py` | `test_submission_guard.py` | ⚪ ⚠️ NOT RUN |
| `services/week_service.py` | `test_week_workflow.py` | ⚪ ⚠️ NOT RUN |
| `utils/date_utils.py` | `test_date_utils.py` | ⚪ ⚠️ NOT RUN |

## Backend: קבצים ללא טסטים ⚪

| קובץ קוד | תיקייה |
|---|---|
| `bot_instance.py` | `app/bot` |
| `inline_kb.py` | `app/bot/keyboards` |
| `auth.py` | `app/bot/middlewares` |
| `admin_admins_controller.py` | `app/controllers` |
| `admin_settings_controller.py` | `app/controllers` |
| `database.py` | `app` |
| `dependencies.py` | `app` |
| `exceptions.py` | `app` |
| `logging_config.py` | `app` |
| `messages.py` | `app` |
| `base.py` | `app/models` |
| `base_repository.py` | `app/repositories` |
| `admin_service.py` | `app/services` |
| `auth_service.py` | `app/services` |
| `deviation_service.py` | `app/services` |
| `event_service.py` | `app/services` |
| `settings_service.py` | `app/services` |
| `submission_service.py` | `app/services` |
| `user_service.py` | `app/services` |
| `telegram_auth.py` | `app/utils` |

## Frontend: מיפוי טסטים

| תת-פרויקט | קובץ קוד | קובץ טסט | סטטוס |
|---|---|---|---|
| admin | `src/api/adminApiClient.js` | `tests/apiClient.test.js` | — |
| admin | `src/components/EventForm.jsx` | `tests/components.test.jsx` | — |
| admin | `src/components/ProtectedRoute.jsx` | `tests/components.test.jsx` | — |
| admin | `src/components/StatusGrid.jsx` | `tests/components.test.jsx` | — |
| admin | `src/components/Navbar.jsx` | `tests/components.test.jsx` | — |
| admin | `src/components/WeekStatusControl.jsx` | `tests/components.test.jsx` | — |
| admin | `src/components/ConfirmDialog.jsx` | `tests/components.test.jsx` | — |
| admin | `src/components/GuardForm.jsx` | `tests/components.test.jsx` | — |
| admin | `src/components/GuardTable.jsx` | `tests/components.test.jsx` | — |
| admin | `src/utils/messages.js` | `tests/messages.test.js` | — |
| webapp | `src/api/apiClient.js` | `tests/apiClient.test.js` | — |
| webapp | `src/components/SubmissionForm.jsx` | `tests/components.test.jsx` | — |
| webapp | `src/components/DayRow.jsx` | `tests/components.test.jsx` | — |
| webapp | `src/components/LockBanner.jsx` | `tests/components.test.jsx` | — |
| webapp | `src/utils/messages.js` | `tests/messages.test.js` | — |

## Backend: רשימת קבצי טסט

| קובץ טסט | מכסה קבצי קוד | סטטוס |
|---|---|---|
| `test_bot.py` | 4 | ⚪ |
| `test_config.py` | 1 | ⚪ |
| `test_controllers.py` | 7 | ⚪ |
| `test_current_week.py` | 2 | ⚪ |
| `test_date_utils.py` | 1 | ⚪ |
| `test_e2e.py` | 1 | ⚪ |
| `test_export.py` | 2 | ⚪ |
| `test_health.py` | 1 | ⚪ |
| `test_initial_seed.py` | 1 | ⚪ |
| `test_models.py` | 8 | 🔴 |
| `test_notification_on_open.py` | 2 | ⚪ |
| `test_open_week.py` | 2 | ⚪ |
| `test_repositories.py` | 6 | 🔴 |
| `test_schemas.py` | 5 | 🔴 |
| `test_status_transitions.py` | 2 | ⚪ |
| `test_submission_guard.py` | 2 | ⚪ |
| `test_week_workflow.py` | 2 | ⚪ |
