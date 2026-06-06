# Feature: Week Workflow — Admin-Driven Status Management + Telegram Bot Integration

## Overview

Replace CRON-based scheduling with admin-driven week lifecycle. The admin controls the submission window via 3 status buttons. When opened, guards receive Telegram notifications. Guards submit constraints in the WebApp for the upcoming Sunday–Saturday week.

## User Stories (Hebrew)

1. **אדמין לוחץ "פתוח להגשה"** → נוצר שבוע חדש (ראשון הבא עד שבת) עם סטטוס `open` → כל השומרים מקבלים הודעה בבוט הטלגרם שאפשר להגיש אילוצים.
2. **שומר מגיש אילוצים** → נכנס ל-webapp, ממלא אילוצים לימים א'-ש' של השבוע הפתוח, שומר.
3. **אדמין לוחץ "סגור להגשה"** → הסטטוס עובר ל-`locked` → אף אחד לא יכול לערוך/להגיש.
4. **אדמין לוחץ "פורסם"** → הסטטוס עובר ל-`published` → לצפייה בלבד.
5. **אדמין לוחץ "פתוח להגשה" שוב** → נוצר שבוע חדש לראשון הבא, וחוזר חלילה.

## Business Rules

- Dates are always **next Sunday to Saturday** (Israel timezone, UTC+3).
- Only **one** week can be in `open` status at a time.
- Status transitions: `open → locked → published`. Then a new week can be opened.
- When admin opens a week, if a week already exists and is `open`, return error (or handle gracefully).
- Guards can **edit** submissions while status is `open`.
- Guards **cannot** submit/edit when status is `locked` or `published`.
- When status changes to `open`, send Telegram notification to all registered guards.
- WebApp shows the submission form only when there's an `open` week.
- WebApp shows a lock banner when no week is open.

## Current Codebase State

### Already Implemented
- `ScheduleWeek` model with `status` column (open/locked/published) — `backend/app/models/schedule_week.py`
- `WeekStatus` enum — `backend/app/constants.py`
- `WeeklySubmission` model — `backend/app/models/weekly_submission.py`
- `WeekService` with `create_week()`, `change_week_status()`, `get_all_weeks()` — `backend/app/services/week_service.py`
- `admin_weeks_controller` with CRUD + status PATCH — `backend/app/controllers/admin_weeks_controller.py`
- `WeekStatusControl` component (3 buttons) — `frontend/admin/src/components/WeekStatusControl.jsx`
- `StatusGrid` component — `frontend/admin/src/components/StatusGrid.jsx`
- `WeeksPage` in admin — `frontend/admin/src/pages/WeeksPage.jsx`
- `useWeeks` hook — `frontend/admin/src/hooks/useWeeks.js`
- `SubmissionForm` in webapp — `frontend/webapp/src/components/SubmissionForm.jsx`
- `LockBanner` in webapp — `frontend/webapp/src/components/LockBanner.jsx`
- `useSubmission` hook — `frontend/webapp/src/hooks/useSubmission.js`
- `apiClient` (webapp) — `frontend/webapp/src/api/apiClient.js`
- `adminApiClient` — `frontend/admin/src/api/adminApiClient.js`
- `SubmissionController` — `backend/app/controllers/submission_controller.py`
- `SubmissionService` — `backend/app/services/submission_service.py`
- `SubmissionRepository` — `backend/app/repositories/submission_repository.py`
- `notifications.py` (bot notifications) — `backend/app/bot/notifications.py`
- `bot_router.py` — `backend/app/bot/bot_router.py`
- `ScheduleWeekRepository` — `backend/app/repositories/schedule_week_repository.py` (if exists) or through base repo
- `week_schemas` — `backend/app/schemas/week_schemas.py`
- `submission_schemas` — `backend/app/schemas/submission_schemas.py`
- `messages.py` — `backend/app/messages.py`
- User model with `telegram_id` field — `backend/app/models/user.py`
- `UserRepository` — `backend/app/repositories/user_repository.py`
- `UserService` — `backend/app/services/user_service.py`

### What Needs to Change / Be Added

#### 1. Backend — `WeekService.open_new_week()`
New method that:
- Validates no other week is currently `open`
- Calculates next Sunday's date (Israel timezone)
- Creates `ScheduleWeek` with dates Sun–Sat, status `open`
- Triggers Telegram notification to all guards
- Returns the created week

#### 2. Backend — `WeekService.change_week_status()`
Update existing method to:
- Validate status transitions (open→locked→published only)
- When transitioning to `open`, call the notification logic
- When transitioning to `locked`, optionally notify guards that submissions are closed

#### 3. Backend — Notification Integration
In `notifications.py` or a new service:
- `notify_week_opened(week)` → send message to all guards via bot
- `notify_week_locked(week)` → optional notification
- Message should include the week dates and a link to the webapp

#### 4. Backend — `SubmissionController` & `SubmissionService`
- `GET /submit` → return submission only if current open week matches
- `POST /submit` → validate week is `open` before accepting
- `PUT /submit` → validate week is `open` before allowing edit
- Return appropriate error if week is `locked` or `published`

#### 5. Backend — New endpoint `GET /weeks/current`
For the webapp to know which week is open:
- Returns the currently open week (dates, status)
- Returns `null` if no week is open
- This tells the webapp whether to show the form or a lock banner

#### 6. Admin Frontend — `WeekStatusControl.jsx`
Update to:
- "פתוח להגשה" button → calls `POST /admin/weeks` (auto-creates next Sun–Sat week) OR a new `POST /admin/weeks/open` endpoint
- "סגור להגשה" button → calls `PATCH /admin/weeks/{id}/status` with `locked`
- "פורסם" button → calls `PATCH /admin/weeks/{id}/status` with `published`
- Show current week info (dates, status)
- Disable buttons based on current status (e.g., can't click "סגור" if already locked)

#### 7. WebApp Frontend — Submission Flow
- On load, call `GET /weeks/current` to check if a week is open
- If open → show `SubmissionForm` with the week's dates
- If not open → show `LockBanner` with appropriate message
- `SubmissionForm` sends `week_id` with submission data
- Disable save/submit button if week is not open (defensive)

#### 8. Telegram Bot — Notification Handler
- When week opens, bot sends message to each guard:
  ```
  🔔 הגשת אילוצים נפתחה!
  תאריכים: {start_date} - {end_date}
  לחץ כאן להגשה: {webapp_url}
  ```
- Use existing `notifications.py` broadcast mechanism

## API Endpoints Summary

### Existing (may need updates)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/weeks` | List all weeks |
| POST | `/admin/weeks` | Create week manually |
| GET | `/admin/weeks/{id}` | Get specific week |
| PATCH | `/admin/weeks/{id}/status` | Change status |
| GET | `/submit` | Get user's submission |
| POST | `/submit` | Create submission |
| PUT | `/submit` | Update submission |

### New
| Method | Path | Description |
|--------|------|-------------|
| POST | `/admin/weeks/open` | Open new week (auto-calculate dates, notify guards) |
| GET | `/weeks/current` | Get currently open week (for webapp) |

## Date Calculation Logic

"האילוצים תמיד מתחילים מיום א' הבא" — always from the **upcoming** Sunday (nearest future Sunday).
If today is Sunday, skip to next week's Sunday (admin opens submission a few days before the target week).

Example: Today is June 2 (Monday) → next Sunday = June 7 → week = June 7–13.

```python
from datetime import date, timedelta

def upcoming_sunday(today: date = None) -> date:
    """Return the next Sunday that is strictly in the future."""
    today = today or date.today()
    days_ahead = (6 - today.weekday()) % 7  # weekday(): Mon=0 .. Sun=6
    if days_ahead == 0:
        days_ahead = 7  # today is Sunday → use next week
    return today + timedelta(days=days_ahead)

def week_end(sunday: date) -> date:
    """Saturday is 6 days after Sunday."""
    return sunday + timedelta(days=6)
```

Verification:
- Monday → days_ahead = 6 → Sunday in 6 days ✓
- Saturday → days_ahead = 1 → Sunday tomorrow ✓
- Sunday → days_ahead = 0 → +7 = next week's Sunday ✓

## Files to Modify/Create

### Backend
1. **`backend/app/services/week_service.py`** — Add `open_new_week()`, update `change_week_status()`
2. **`backend/app/controllers/admin_weeks_controller.py`** — Add `POST /admin/weeks/open` endpoint
3. **`backend/app/controllers/submission_controller.py`** — Add `GET /weeks/current`, add status validation
4. **`backend/app/services/submission_service.py`** — Add status validation in create/update
5. **`backend/app/bot/notifications.py`** — Add `notify_week_opened()`, `notify_week_locked()`
6. **`backend/app/messages.py`** — Add notification message templates
7. **`backend/app/schemas/week_schemas.py`** — Add `CurrentWeekResponse` schema if needed

### Frontend Admin
8. **`frontend/admin/src/components/WeekStatusControl.jsx`** — Wire buttons to API calls with proper logic
9. **`frontend/admin/src/hooks/useWeeks.js`** — Add `openNewWeek()` function
10. **`frontend/admin/src/api/adminApiClient.js`** — Add `openNewWeek()` API call

### Frontend WebApp
11. **`frontend/webapp/src/api/apiClient.js`** — Add `getCurrentWeek()` function
12. **`frontend/webapp/src/hooks/useSubmission.js`** — Fetch current week, handle locked state
13. **`frontend/webapp/src/App.jsx`** — Show form or lock banner based on week status
14. **`frontend/webapp/src/components/LockBanner.jsx`** — Update message based on status

### Tests
15. **`backend/tests/test_week_workflow.py`** — New test file for the workflow
16. Update existing tests as needed

## Implementation Order

1. Backend: `WeekService.open_new_week()` + date calculation
2. Backend: `POST /admin/weeks/open` endpoint
3. Backend: `GET /weeks/current` endpoint  
4. Backend: Notification integration
5. Backend: Submission status validation
6. Admin frontend: Wire WeekStatusControl buttons
7. WebApp frontend: Current week check + lock/form logic
8. Tests