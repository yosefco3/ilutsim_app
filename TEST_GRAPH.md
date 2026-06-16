# Test Coverage Graph

_נוצר אוטומטית ב: 2026-06-16 19:54_
**טרנד:**  ↓5%

## סיכום

| מדד | ערך |
|---|---|
| קבצי קוד backend | 67 |
| קבצי קוד מכוסים בטסטים | 33 |
| קבצי קוד ללא טסטים | 34 |
| אחוז כיסוי | 49% ↓5% |
| טסטים עוברים (backend) | 35 ✅ |
| טסטים נכשלים (backend) | 0 ❌ |
| קבצי קוד frontend (ממופים) | 10 |
| טסטים עוברים (frontend) | 27 ✅ |
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
| `controllers/admin_weeks_controller.py` | `test_open_week.py` | ⚪ ⚠️ NOT RUN |
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
| `services/week_service.py` | `test_open_week.py` | ⚪ ⚠️ NOT RUN |
| `services/week_service.py` | `test_status_transitions.py` | 🟢 PASS |
| `services/week_service.py` | `test_submission_guard.py` | 🟢 PASS |
| `services/week_service.py` | `test_week_workflow.py` | 🟢 PASS |
| `utils/date_utils.py` | `test_date_utils.py` | 🟢 PASS |

## Backend: קבצים ללא טסטים (מדורגים לפי חשיבות)

| עדיפות | קובץ קוד | תיקייה |
|---|---|---|
| 🔴 HIGH | `admin_admins_controller.py` | `app/controllers` |
| 🔴 HIGH | `admin_settings_controller.py` | `app/controllers` |
| 🔴 HIGH | `constraints_import_controller.py` | `app/controllers` |
| 🔴 HIGH | `base_repository.py` | `app/repositories` |
| 🔴 HIGH | `admin_service.py` | `app/services` |
| 🔴 HIGH | `auth_service.py` | `app/services` |
| 🔴 HIGH | `commit.py` | `app/services/constraints_import` |
| 🔴 HIGH | `hours.py` | `app/services/constraints_import` |
| 🔴 HIGH | `parser.py` | `app/services/constraints_import` |
| 🔴 HIGH | `preview.py` | `app/services/constraints_import` |
| 🔴 HIGH | `deviation_service.py` | `app/services` |
| 🔴 HIGH | `settings_service.py` | `app/services` |
| 🔴 HIGH | `submission_service.py` | `app/services` |
| 🔴 HIGH | `user_service.py` | `app/services` |
| 🟡 MEDIUM | `inline_kb.py` | `app/bot/keyboards` |
| 🟡 MEDIUM | `auth.py` | `app/bot/middlewares` |
| 🟡 MEDIUM | `webapp.py` | `app/bot` |
| 🟡 MEDIUM | `profile_controller.py` | `app/schedule_builder/controllers` |
| 🟡 MEDIUM | `activation_profile.py` | `app/schedule_builder/models` |
| 🟡 MEDIUM | `profile_repository.py` | `app/schedule_builder/repositories` |
| 🟡 MEDIUM | `profile_schemas.py` | `app/schedule_builder/schemas` |
| 🟡 MEDIUM | `profile_service.py` | `app/schedule_builder/services` |
| 🟡 MEDIUM | `scheduler.py` | `app` |
| 🟡 MEDIUM | `constraints_import.py` | `app/schemas` |
| 🟡 MEDIUM | `telegram_auth.py` | `app/utils` |
| 🟡 MEDIUM | `version.py` | `app` |
| ⚪ LOW | `bot_instance.py` | `app/bot` |
| ⚪ LOW | `database.py` | `app` |
| ⚪ LOW | `dependencies.py` | `app` |
| ⚪ LOW | `exceptions.py` | `app` |
| ⚪ LOW | `logging_config.py` | `app` |
| ⚪ LOW | `messages.py` | `app` |
| ⚪ LOW | `base.py` | `app/models` |
| ⚪ LOW | `dependencies.py` | `app/schedule_builder` |

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
| `test_activation_profile_model.py` | 1 | 🟢 |
| `test_admin_published_guard.py` | 1 | 🟢 |
| `test_admin_submission.py` | 1 | 🟢 |
| `test_auto_advance.py` | 1 | 🟢 |
| `test_auto_rotate.py` | 1 | 🟢 |
| `test_bot.py` | 4 | 🟢 |
| `test_config.py` | 1 | 🟢 |
| `test_constraint_rules_endpoint.py` | 1 | 🟢 |
| `test_constraints_hours.py` | 1 | 🟢 |
| `test_constraints_parser.py` | 1 | 🟢 |
| `test_controllers.py` | 7 | 🟢 |
| `test_current_week.py` | 2 | 🟢 |
| `test_date_utils.py` | 1 | 🟢 |
| `test_e2e.py` | 1 | ⚪ |
| `test_export.py` | 2 | 🟢 |
| `test_health.py` | 1 | 🟢 |
| `test_import_commit.py` | 1 | 🟢 |
| `test_import_preview_endpoint.py` | 1 | 🟢 |
| `test_initial_seed.py` | 1 | 🟢 |
| `test_models.py` | 8 | 🟢 |
| `test_notification_on_open.py` | 2 | 🟢 |
| `test_profile_api.py` | 1 | 🟢 |
| `test_profile_service.py` | 1 | 🟢 |
| `test_repositories.py` | 6 | 🟢 |
| `test_retention.py` | 1 | 🟢 |
| `test_scheduler.py` | 1 | 🟢 |
| `test_schemas.py` | 5 | 🟢 |
| `test_settings_service.py` | 1 | 🟢 |
| `test_status_transitions.py` | 2 | 🟢 |
| `test_submission_guard.py` | 2 | 🟢 |
| `test_submission_notification.py` | 1 | 🟢 |
| `test_submission_persistence.py` | 1 | 🟢 |
| `test_telegram_auth.py` | 1 | 🟢 |
| `test_telegram_token_apply.py` | 1 | 🟢 |
| `test_webapp_url.py` | 1 | 🟢 |
| `test_week_workflow.py` | 2 | 🟢 |
