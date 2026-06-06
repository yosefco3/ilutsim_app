# Test Coverage Graph

_נוצר אוטומטית ב: 2026-06-06 19:46_

## סיכום

| מדד | ערך |
|---|---|
| קבצי קוד backend | 57 |
| קבצי קוד מכוסים בטסטים | 37 |
| קבצי קוד ללא טסטים | 20 |
| אחוז כיסוי | 64% |

## Backend: מיפוי קוד → טסטים

| קובץ קוד | קובץ טסט | סטטוס |
|---|---|---|
| `bot/bot_router.py` | `test_bot.py` | — |
| `bot/core.py` | `test_bot.py` | — |
| `bot/cron.py` | `test_bot.py` | — |
| `bot/notifications.py` | `test_bot.py` | — |
| `bot/notifications.py` | `test_notification_on_open.py` | — |
| `config.py` | `test_config.py` | — |
| `constants.py` | `test_status_transitions.py` | — |
| `controllers/admin_events_controller.py` | `test_controllers.py` | — |
| `controllers/admin_export_controller.py` | `test_controllers.py` | — |
| `controllers/admin_export_controller.py` | `test_export.py` | — |
| `controllers/admin_notifications_controller.py` | `test_controllers.py` | — |
| `controllers/admin_users_controller.py` | `test_controllers.py` | — |
| `controllers/admin_weeks_controller.py` | `test_controllers.py` | — |
| `controllers/admin_weeks_controller.py` | `test_open_week.py` | — |
| `controllers/auth_controller.py` | `test_controllers.py` | — |
| `controllers/submission_controller.py` | `test_controllers.py` | — |
| `controllers/submission_controller.py` | `test_submission_guard.py` | — |
| `main.py` | `test_e2e.py` | — |
| `main.py` | `test_health.py` | — |
| `models/admin.py` | `test_models.py` | — |
| `models/daily_status.py` | `test_models.py` | — |
| `models/schedule_event.py` | `test_models.py` | — |
| `models/schedule_week.py` | `test_models.py` | — |
| `models/shift_window.py` | `test_models.py` | — |
| `models/system_setting.py` | `test_models.py` | — |
| `models/user.py` | `test_models.py` | — |
| `models/weekly_submission.py` | `test_models.py` | — |
| `repositories/admin_repository.py` | `test_repositories.py` | — |
| `repositories/schedule_event_repository.py` | `test_repositories.py` | — |
| `repositories/schedule_week_repository.py` | `test_current_week.py` | — |
| `repositories/schedule_week_repository.py` | `test_repositories.py` | — |
| `repositories/schedule_week_repository.py` | `test_week_workflow.py` | — |
| `repositories/submission_repository.py` | `test_repositories.py` | — |
| `repositories/system_settings_repository.py` | `test_repositories.py` | — |
| `repositories/user_repository.py` | `test_repositories.py` | — |
| `schemas/common_schemas.py` | `test_schemas.py` | — |
| `schemas/event_schemas.py` | `test_schemas.py` | — |
| `schemas/submission_schemas.py` | `test_schemas.py` | — |
| `schemas/user_schemas.py` | `test_schemas.py` | — |
| `schemas/week_schemas.py` | `test_schemas.py` | — |
| `seed.py` | `test_initial_seed.py` | — |
| `services/excel_export_service.py` | `test_export.py` | — |
| `services/week_service.py` | `test_current_week.py` | — |
| `services/week_service.py` | `test_notification_on_open.py` | — |
| `services/week_service.py` | `test_open_week.py` | — |
| `services/week_service.py` | `test_status_transitions.py` | — |
| `services/week_service.py` | `test_submission_guard.py` | — |
| `services/week_service.py` | `test_week_workflow.py` | — |
| `utils/date_utils.py` | `test_date_utils.py` | — |

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
| `test_bot.py` | 4 | — |
| `test_config.py` | 1 | — |
| `test_controllers.py` | 7 | — |
| `test_current_week.py` | 2 | — |
| `test_date_utils.py` | 1 | — |
| `test_e2e.py` | 1 | — |
| `test_export.py` | 2 | — |
| `test_health.py` | 1 | — |
| `test_initial_seed.py` | 1 | — |
| `test_models.py` | 8 | — |
| `test_notification_on_open.py` | 2 | — |
| `test_open_week.py` | 2 | — |
| `test_repositories.py` | 6 | — |
| `test_schemas.py` | 5 | — |
| `test_status_transitions.py` | 2 | — |
| `test_submission_guard.py` | 2 | — |
| `test_week_workflow.py` | 2 | — |
