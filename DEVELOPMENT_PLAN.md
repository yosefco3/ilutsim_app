# 📋 ספריית פרומפטים - תוכנית פיתוח (Development Plan)
## מערכת Micro-SaaS לניהול אילוצים ומשמרות אבטחה

---

## סקירת ארכיטקטורה כללית

```
┌─────────────────────────────────────────────────────────┐
│                    Telegram Bot (aiogram)                │
│              (אימות, התראות, תקשורת עם שומרים)           │
├─────────────────────────────────────────────────────────┤
│              Telegram Web App (Frontend SPA)             │
│           (טופס הגשת אילוצים שבועי - React/Vue)         │
├─────────────────────────────────────────────────────────┤
│              Admin Dashboard (Frontend SPA)              │
│         (ניהול שומרים, שבועות, ייצוא אקסל)              │
├─────────────────────────────────────────────────────────┤
│                FastAPI Backend (Python)                  │
│     Controllers → Services → Repositories (OOP)         │
├─────────────────────────────────────────────────────────┤
│         PostgreSQL + SQLAlchemy ORM + Alembic            │
└─────────────────────────────────────────────────────────┘
```

---

## שלב 0 — תשתית הפרויקט, קונפיגורציה, לוגים ותשתית בדיקות

### מטרה:
הקמת מבנה התיקיות של הפרויקט, הגדרת קבצי קונפיגורציה, משתני סביבה, מערכת לוגים מרכזית, קובץ ריכוז הודעות, ותשתית הבדיקות. זהו הבסיס שעליו ייבנו כל השלבים הבאים.

### פרומפט:

```
אתה פועל כארכיטקט תוכנה בכיר ומפתח Full-Stack מומחה.

צור את מבנה התיקיות הבסיסי לפרויקט Micro-SaaS לניהול אילוצים ומשמרות אבטחה, בהתאם למפרט הטכני הבא:

**מבנה הפרויקט (Backend - Python/FastAPI):**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app factory + lifespan
│   ├── config.py                # Settings class (Pydantic BaseSettings, reads .env)
│   ├── database.py              # Async engine + session factory
│   ├── logging_config.py        # Structured logging setup (JSON format)
│   ├── messages.py              # ריכוז כל הטקסטים והודעות המערכת בעברית
│   ├── constants.py             # Enums, default values, shift types
│   ├── dependencies.py          # Dependency injection (DB session, current user, etc.)
│   ├── exceptions.py            # Custom exception classes + global handlers
│   ├── controllers/             # Route handlers (thin layer, delegates to services)
│   │   └── __init__.py
│   ├── services/                # Business logic layer
│   │   └── __init__.py
│   ├── repositories/            # Data access layer (SQLAlchemy queries)
│   │   └── __init__.py
│   ├── models/                  # SQLAlchemy ORM models
│   │   └── __init__.py
│   ├── schemas/                 # Pydantic v2 request/response schemas
│   │   └── __init__.py
│   ├── bot/                     # Telegram bot (aiogram)
│   │   └── __init__.py
│   └── utils/                   # Shared utilities
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures: test DB, async session, test client
│   ├── test_config.py           # Tests for config loading
│   ├── test_messages.py         # Tests for messages completeness
│   ├── test_constants.py        # Tests for enums
│   └── test_exceptions.py       # Tests for exception handlers
├── alembic/                     # DB migrations
│   └── ...
├── alembic.ini
├── requirements.txt
├── requirements-dev.txt         # Test dependencies
├── pyproject.toml               # Pytest configuration
├── .env.example
├── .gitignore
└── Dockerfile
```

**דרישות מפורטות:**

1. **config.py**: מחלקת `Settings` שיורשת מ-`pydantic_settings.BaseSettings`. חייבת לכלול:
   - `DATABASE_URL` (PostgreSQL async URL)
   - `DATABASE_URL_SYNC` (for Alembic)
   - `TELEGRAM_BOT_TOKEN`
   - `WEBAPP_URL` (כתובת ה-Web App)
   - `ADMIN_DASHBOARD_URL`
   - `LOG_LEVEL` (ברירת מחדל: INFO)
   - `ENVIRONMENT` (dev/staging/production)
   - `CRON_WEEKLY_OPEN_DAY` (יום שליחת התראות, ברירת מחדל: "sunday")
   - `CRON_WEEKLY_OPEN_HOUR` (שעת שליחה, ברירת מחדל: "09:00")
   - כל ערך נקרא מקובץ `.env`, אין hard coding.
   - פונקציית `get_settings()` עם lru_cache

2. **database.py**: הגדרת `create_async_engine`, `async_sessionmaker`, ופונקציית `get_db_session()` (async generator).

3. **logging_config.py**: פונקציית `setup_logging()` שמגדירה structured logging עם JSON formatter, כולל rotation. תומך ב-log levels שונים לפי סביבה.

4. **messages.py**: מחלקת `Messages` (או dataclass frozen) שמרכזת את **כל** הטקסטים בעברית של המערכת. כולל:
   - הודעות הבוט: BOT_WELCOME, BOT_AUTH_SUCCESS, BOT_AUTH_FAIL, BOT_WEEK_OPEN, BOT_REMINDER, BOT_SUBMISSION_SUMMARY, BOT_DEVIATION_WARNING, BOT_LOCKOUT, BOT_SUBMIT_ANYWAY
   - הודעות שגיאה: ERR_WEEK_LOCKED, ERR_USER_NOT_FOUND, ERR_USER_DEACTIVATED, ERR_AUTH_FAILED, ERR_CONFLICT
   - Labels ל-UI: LABEL_AVAILABLE, LABEL_UNAVAILABLE, LABEL_BLOCKED, LABEL_MORNING, LABEL_AFTERNOON, LABEL_NIGHT
   - Labels לאקסל: EXCEL_HEADER_NAME, EXCEL_HEADER_PHONE, etc.
   - כל טקסט הוא class variable/constant — לא פזור בקוד.

5. **constants.py**: Enums עבור:
   - `ShiftType` (morning, afternoon, night)
   - `WeekStatus` (open, locked, published)
   - `EventType` (vacation, military_reserve, firearms_training)
   - `SubmissionStatus` (submitted, submitted_with_variance, pending, auto_absence)
   - `UserRole` (guard, shift_lead, scanner)

6. **exceptions.py**: מחלקות Exception מותאמות:
   - `AppBaseException` (base class עם status_code ו-message)
   - `WeekLockedException(AppBaseException)` — 403
   - `UserNotAuthorizedException(AppBaseException)` — 401
   - `UserDeactivatedException(AppBaseException)` — 403
   - `UserNotFoundException(AppBaseException)` — 404
   - `ValidationException(AppBaseException)` — 422
   - `ConflictException(AppBaseException)` — 409
   - פונקציות Global exception handlers ל-FastAPI שמחזירות תשובות JSON מסודרות (שימוש בהודעות מ-messages.py).

7. **dependencies.py**: פונקציות Dependency Injection:
   - `get_db()` — async generator ל-SQLAlchemy AsyncSession (מ-database.py)
   - `get_current_user()` — placeholder לאימות Telegram initData (ייבנה בשלב 5)

8. **main.py**: FastAPI app factory עם lifespan handler (startup/shutdown), middleware ללוגים, CORS configuration.

9. **.env.example**: קובץ דוגמה עם כל המשתנים הנדרשים (ערכים לדוגמה בלבד).

10. **requirements.txt**: כל התלויות — fastapi, uvicorn[standard], sqlalchemy[asyncio], asyncpg, pydantic-settings, aiogram, openpyxl, alembic, python-dotenv, apscheduler.

11. **requirements-dev.txt**: תלויות פיתוח — pytest, pytest-asyncio, pytest-cov, httpx, aiosqlite, factory-boy, freezegun.

12. **pyproject.toml**: הגדרות pytest — asyncio_mode = "auto", testpaths, filterwarnings.

**בדיקות נדרשות (tests/):**

13. **conftest.py**:
    - Fixture `test_settings` — יוצר Settings עם ערכי test (DB SQLite async)
    - Fixture `test_engine` — async engine ל-SQLite (aiosqlite)
    - Fixture `test_session` — AsyncSession מ-test engine
    - Fixture `test_app` — FastAPI test app
    - Fixture `test_client` — httpx.AsyncClient

14. **test_config.py**:
    - טסט שה-Settings נטען נכון מ-env vars
    - טסט שכל השדות הנדרשים קיימים
    - טסט שברירות מחדל עובדות (LOG_LEVEL=INFO, ENVIRONMENT=dev)

15. **test_messages.py**:
    - טסט שכל ה-attributes של Messages אינם ריקים
    - טסט שכל הטקסטים בעברית (מכילים תווים עבריים)
    - טסט שאין attributes כפולים

16. **test_constants.py**:
    - טסט שכל Enum מכיל את הערכים הצפויים
    - טסט ש-ShiftType.morning, afternoon, night קיימים
    - טסט ש-WeekStatus.open, locked, published קיימים

17. **test_exceptions.py**:
    - טסט שכל exception מחזיר status code נכון
    - טסט שה-global handlers מחזירים JSON תקין
    - טסט שהודעות השגיאה מגיעות מ-messages.py

**כללים:**
- OOP מלא עם הפרדת שכבות (Controllers → Services → Repositories)
- אפס hard coding — כל ערך קונפיגורבילי
- כל טקסט בעברית מרוכז ב-messages.py
- Error handling ולוגים מהיום הראשון
- Type hints מלאים בכל מקום
- Async/await בכל מקום שרלוונטי
- כל הטסטים רצים עם `pytest` ועוברים
```

---

## שלב 1 — מודלים של בסיס הנתונים (SQLAlchemy ORM), מיגרציות (Alembic) ובדיקות

### מטרה:
יצירת כל מודלי ה-ORM לפי סכמת ה-DB מהמפרט, כולל relationships, indexes, הגדרת Alembic למיגרציות, ובדיקות שהמודלים תקינים.

### פרומפט:

```
אתה ממשיך בפיתוח מערכת ניהול אילוצים ומשמרות אבטחה. שלב 0 (תשתית, config, logging, messages, test infrastructure) הושלם.

כעת צור את כל מודלי ה-SQLAlchemy ORM, תשתית Alembic, ובדיקות — בהתאם לסכמת ה-DB מהמפרט:

**מודלים נדרשים (בתיקיית `app/models/`):**

1. **base.py**: Base class משותף עם:
   - `id` (UUID, primary key, default uuid4)
   - `created_at`, `updated_at` timestamps אוטומטיים
   - `__tablename__` auto-generated מ-class name

2. **user.py** — טבלת `users`:
   - `phone_number` (unique, not null)
   - `telegram_id` (unique, nullable)
   - `full_name` (not null)
   - `role` (Enum: UserRole, not null)
   - `is_active` (boolean, default True)
   - `exemptions_notes` (text, nullable)
   - `min_total_shifts` (integer, default 0)
   - `min_night_shifts` (integer, default 0)
   - `min_evening_shifts` (integer, default 0)
   - Relationships: schedule_events, weekly_submissions

3. **schedule_week.py** — טבלת `schedule_weeks`:
   - `start_date` (date, not null)
   - `end_date` (date, not null)
   - `status` (Enum: WeekStatus, default 'open')
   - Relationship: weekly_submissions

4. **schedule_event.py** — טבלת `schedule_events`:
   - `user_id` (FK → users.id)
   - `event_type` (Enum: EventType, not null)
   - `start_date`, `end_date` (date, not null)
   - Relationship: user

5. **weekly_submission.py** — טבלת `weekly_submissions`:
   - `user_id` (FK → users.id)
   - `week_id` (FK → schedule_weeks.id)
   - `general_notes` (text, nullable)
   - `has_deviation` (boolean, default False)
   - `submitted_at` (timestamp, not null, auto-set on create/update)
   - Unique constraint: (user_id, week_id) — למנוע הגשות כפולות
   - Relationships: user, week, daily_statuses

6. **daily_status.py** — טבלת `daily_statuses`:
   - `submission_id` (FK → weekly_submissions.id, ondelete CASCADE)
   - `date` (date, not null)
   - `is_available` (boolean, not null)
   - Relationship: submission, shift_windows

7. **shift_window.py** — טבלת `shift_windows`:
   - `daily_status_id` (FK → daily_statuses.id, ondelete CASCADE)
   - `shift_type` (Enum: ShiftType, not null)
   - `start_time` (time, not null)
   - `end_time` (time, not null)

8. **system_setting.py** — טבלת `system_settings`:
   - `setting_key` (string, primary key) — **לא יורש מ-Base** (PK הוא string, לא UUID)
   - `setting_value` (string, not null)
   - `description` (string, nullable)
   - `created_at`, `updated_at` timestamps

9. **`__init__.py`**: ייבוא כל המודלים (חשוב ל-Alembic autogenerate)

**Alembic:**
- הגדר `alembic.ini` ו-`alembic/env.py` לעבודה עם async engine
- ה-env.py קורא את DATABASE_URL מה-config (Settings)
- צור את המיגרציה הראשונית (`initial_schema`)
- הוסף seed data למיגרציה: system_settings ברירות מחדל (default_morning_start=07:00, default_morning_end=15:00, default_afternoon_start=15:00, default_afternoon_end=23:00, default_night_start=23:00, default_night_end=07:00)

**בדיקות נדרשות (tests/test_models.py):**

1. **test_create_user** — יצירת user ושמירה ב-DB, ווידוא שכל השדות נשמרו נכון
2. **test_user_unique_phone** — ניסיון ליצור שני users עם אותו phone_number → IntegrityError
3. **test_user_unique_telegram_id** — ניסיון ליצור שני users עם אותו telegram_id → IntegrityError
4. **test_user_default_values** — ווידוא ברירות מחדל (is_active=True, min_total_shifts=0, etc.)
5. **test_create_schedule_week** — יצירת שבוע ובדיקת default status=open
6. **test_create_schedule_event** — יצירת אירוע חסימה + relationship ל-user
7. **test_create_weekly_submission** — יצירת הגשה + unique constraint (user_id, week_id)
8. **test_duplicate_submission** — ניסיון ליצור שתי הגשות לאותו user+week → IntegrityError
9. **test_cascade_delete_submission** — מחיקת submission → daily_statuses ו-shift_windows נמחקים
10. **test_create_full_submission_chain** — יצירת submission → daily_status → shift_window, ובדיקת relationships
11. **test_system_setting_crud** — יצירת, קריאת, עדכון setting
12. **test_uuid_auto_generation** — ווידוא שה-UUID נוצר אוטומטית
13. **test_timestamps_auto_set** — ווידוא שה-created_at ו-updated_at מוגדרים אוטומטית

**כללים:**
- כל המודלים יורשים מ-Base class משותף (חוץ מ-system_settings)
- UUID כ-primary key בכל מקום
- Indexes על שדות שנשאלים תדיר (phone_number, telegram_id, user_id+week_id)
- Cascade delete מתאים (כשמוחקים submission → נמחקים daily_statuses ו-shift_windows)
- Type hints מלאים
- שימוש ב-Mapped ו-mapped_column (SQLAlchemy 2.0 style)
- כל הטסטים רצים עם `pytest` ועוברים
```

---

## שלב 2 — שכבת Repositories (Data Access Layer) ובדיקות

### מטרה:
בניית שכבת הגישה לנתונים — מחלקות Repository לכל ישות, עם פעולות CRUD אסינכרוניות, ובדיקות מקיפות.

### פרומפט:

```
אתה ממשיך בפיתוח המערכת. שלבים 0-1 (תשתית + מודלים) הושלמו. כל הטסטים הקודמים עוברים.

כעת צור את שכבת ה-Repositories (Data Access Layer) בתיקיית `app/repositories/` ואת הבדיקות שלהם:

**מבנה:**

1. **base_repository.py**: מחלקת `BaseRepository[T]` גנרית:
   - מקבלת AsyncSession ב-constructor (Dependency Injection)
   - מתודות משותפות: `get_by_id()`, `get_all()`, `create()`, `update()`, `delete()`, `save()`
   - כל המתודות async
   - Type hints מלאים עם Generics

2. **user_repository.py** — `UserRepository(BaseRepository[User])`:
   - `get_by_phone(phone_number: str) → User | None`
   - `get_by_telegram_id(telegram_id: str) → User | None`
   - `get_active_users() → list[User]`
   - `link_telegram_id(phone_number: str, telegram_id: str) → User`
   - `deactivate_user(user_id: UUID) → User`

3. **schedule_week_repository.py** — `ScheduleWeekRepository`:
   - `get_current_open_week() → ScheduleWeek | None`
   - `get_by_date_range(start: date, end: date) → ScheduleWeek | None`
   - `update_status(week_id: UUID, new_status: WeekStatus) → ScheduleWeek`

4. **schedule_event_repository.py** — `ScheduleEventRepository`:
   - `get_events_for_user(user_id: UUID, start_date: date, end_date: date) → list[ScheduleEvent]`
   - `get_full_week_absences(week_start: date, week_end: date) → list[ScheduleEvent]` (אירועים שמכסים שבוע שלם)
   - `create_event(user_id: UUID, event_type: EventType, start: date, end: date) → ScheduleEvent`
   - `delete_event(event_id: UUID) → bool`

5. **submission_repository.py** — `SubmissionRepository`:
   - `get_submission(user_id: UUID, week_id: UUID) → WeeklySubmission | None` (eager load: daily_statuses → shift_windows)
   - `upsert_submission(user_id: UUID, week_id: UUID, data: dict) → WeeklySubmission` (Upsert מלא — מחיקת daily_statuses ישנים + יצירה חדשה)
   - `get_submissions_for_week(week_id: UUID) → list[WeeklySubmission]`
   - `get_missing_submissions(week_id: UUID, active_user_ids: list[UUID]) → list[UUID]` (מזהי שומרים שלא הגישו)
   - `get_submission_stats(week_id: UUID) → dict` (count: submitted, pending, variance, auto_absence)

6. **system_settings_repository.py** — `SystemSettingsRepository`:
   - `get_setting(key: str) → str | None`
   - `set_setting(key: str, value: str, description: str = None)`
   - `get_all_settings() → dict[str, str]`
   - `get_default_shift_times() → dict` (מחזיר dict עם שעות ברירת מחדל לכל סוג משמרת)

7. **`__init__.py`**: ייבוא כל ה-repositories

**בדיקות נדרשות (tests/test_repositories.py):**

**UserRepository:**
1. `test_create_and_get_user` — יצירה ושליפה לפי ID
2. `test_get_by_phone_found` — שליפה לפי טלפון — נמצא
3. `test_get_by_phone_not_found` — שליפה לפי טלפון — לא נמצא → None
4. `test_get_by_telegram_id` — שליפה לפי telegram_id
5. `test_get_active_users` — מחזיר רק פעילים (לא inactive)
6. `test_link_telegram_id` — קישור telegram_id למשתמש קיים
7. `test_link_telegram_id_not_found` — ניסיון לקשר לטלפון שלא קיים
8. `test_deactivate_user` — השבתת משתמש, ווידוא is_active=False

**ScheduleWeekRepository:**
9. `test_create_and_get_week` — יצירה ושליפה
10. `test_get_current_open_week` — שליפת שבוע פתוח
11. `test_get_current_open_week_none` — אין שבוע פתוח → None
12. `test_update_status` — שינוי סטטוס מ-open ל-locked

**ScheduleEventRepository:**
13. `test_create_event` — יצירת אירוע חסימה
14. `test_get_events_for_user_in_range` — שליפת אירועים בטווח תאריכים
15. `test_get_full_week_absences` — שליפת העדרויות מלאות (מכסות שבוע שלם)
16. `test_delete_event` — מחיקת אירוע

**SubmissionRepository:**
17. `test_upsert_submission_create` — יצירת הגשה חדשה (insert path)
18. `test_upsert_submission_update` — עדכון הגשה קיימת (upsert path — מחיקה + יצירה)
19. `test_get_submission_with_relations` — שליפה כולל daily_statuses ו-shift_windows (eager loading)
20. `test_get_submissions_for_week` — שליפת כל ההגשות לשבוע
21. `test_get_missing_submissions` — שליפת שומרים שלא הגישו

**SystemSettingsRepository:**
22. `test_get_set_setting` — כתיבה וקריאה של setting
23. `test_get_all_settings` — שליפת כל ההגדרות כ-dict
24. `test_get_default_shift_times` — ווידוא שמחזיר שעות ברירת מחדל נכונות

**כללים:**
- כל repository מקבל session דרך constructor (DI)
- Async/await בכל מקום
- Error handling עם logging מתאים
- אין business logic — רק גישה לנתונים
- Type hints מלאים
- שימוש ב-`select()`, `insert()`, `update()` של SQLAlchemy 2.0
- כל הטסטים משתמשים ב-fixtures מ-conftest.py (test DB)
- כל הטסטים רצים עם `pytest` ועוברים
```

---

## שלב 3 — Pydantic Schemas (Validation Layer) ובדיקות

### מטרה:
יצירת סכמות Pydantic v2 לוולידציה של כל הקלט והפלט של ה-API, ובדיקות מקיפות לוולידציה.

### פרומפט:

```
אתה ממשיך בפיתוח המערכת. שלבים 0-2 (תשתית, מודלים, repositories) הושלמו. כל הטסטים הקודמים עוברים.

כעת צור את סכמות ה-Pydantic v2 בתיקיית `app/schemas/` ואת הבדיקות שלהם:

**קבצים נדרשים:**

1. **user_schemas.py**:
   - `UserCreate` (phone_number, full_name, role, exemptions_notes?, min_total_shifts?, min_night_shifts?, min_evening_shifts?)
   - `UserUpdate` (כל השדות optional)
   - `UserResponse` (כל השדות + id, is_active, telegram_id, created_at)
   - `UserListResponse` (users: list[UserResponse], count: int)

2. **week_schemas.py**:
   - `WeekCreate` (start_date, end_date)
   - `WeekStatusUpdate` (status: WeekStatus)
   - `WeekResponse` (כל השדות + id, status)

3. **event_schemas.py**:
   - `ScheduleEventCreate` (user_id: UUID, event_type: EventType, start_date: date, end_date: date)
   - `ScheduleEventResponse` (כל השדות + id)
   - `BlockedDateInfo` (date: date, event_type: EventType, label: str)

4. **submission_schemas.py** — הסכמה המרכזית:
   - `ShiftWindowInput` (shift_type: ShiftType, start_time: time, end_time: time)
   - `ShiftWindowResponse` (כנ"ל + id)
   - `DayStatusInput` (date: date, is_available: bool, shifts: list[ShiftWindowInput])
   - `DayStatusResponse` (כנ"ל + id, shift_windows)
   - `SubmissionCreate` (week_id: UUID, general_notes: str | None, days: list[DayStatusInput])
   - `SubmissionResponse` (כל הנתונים כולל days ו-shifts, + has_deviation, submitted_at)
   - `SubmissionStatusGrid` (user_id: UUID, full_name: str, phone_number: str, status: SubmissionStatus, submitted_at: datetime | None, has_deviation: bool)
   - `DeviationDetail` (rule_name: str, required: int, actual: int)

5. **settings_schemas.py**:
   - `SystemSettingUpdate` (setting_key: str, setting_value: str, description: str | None)
   - `SystemSettingResponse` (setting_key, setting_value, description)
   - `DefaultShiftTimesResponse` (morning_start: time, morning_end: time, afternoon_start: time, afternoon_end: time, night_start: time, night_end: time)

6. **common_schemas.py**:
   - `ApiResponse` (success: bool, message: str, data: Any | None)
   - `ErrorResponse` (success: bool = False, error: str, detail: str | None)

**ולידציות מיוחדות (validators):**
- `phone_number` — ולידציה של פורמט ישראלי (מתחיל ב-05, 10 ספרות, או +972)
- `start_date` חייב להיות לפני `end_date` (WeekCreate, ScheduleEventCreate)
- ב-`ShiftWindowInput`: `start_time` ≠ `end_time`
- ב-`ShiftWindowInput` למשמרת לילה: `start_time` > `end_time` (חוצה חצות) — מותר
- ב-`DayStatusInput`: אם `is_available=False`, רשימת `shifts` חייבת להיות ריקה
- ב-`DayStatusInput`: אם `is_available=True`, חייבת להיות לפחות משמרת אחת
- ב-`SubmissionCreate`: `days` חייב להכיל לפחות יום אחד

**בדיקות נדרשות (tests/test_schemas.py):**

**UserSchemas:**
1. `test_user_create_valid` — יצירת UserCreate עם נתונים תקינים
2. `test_user_create_invalid_phone` — טלפון לא תקין → ValidationError
3. `test_user_create_valid_phone_formats` — פורמטים שונים: "0501234567", "+972501234567"
4. `test_user_update_partial` — עדכון חלקי (רק שם)
5. `test_user_response_from_orm` — המרה מ-ORM model ל-response

**WeekSchemas:**
6. `test_week_create_valid` — תאריכים תקינים
7. `test_week_create_end_before_start` — end_date לפני start_date → ValidationError
8. `test_week_status_update_valid_enum` — סטטוס תקין
9. `test_week_status_update_invalid_enum` — סטטוס לא קיים → ValidationError

**SubmissionSchemas:**
10. `test_submission_create_valid_full` — הגשה מלאה עם ימים ומשמרות
11. `test_submission_create_unavailable_no_shifts` — יום לא זמין בלי shifts — תקין
12. `test_submission_create_unavailable_with_shifts` — יום לא זמין עם shifts → ValidationError
13. `test_submission_create_available_no_shifts` — יום זמין בלי shifts → ValidationError
14. `test_shift_window_night_crosses_midnight` — משמרת לילה 23:00-07:00 — תקין
15. `test_shift_window_same_start_end` — start=end → ValidationError
16. `test_submission_create_empty_days` — רשימת ימים ריקה → ValidationError

**EventSchemas:**
17. `test_event_create_valid` — אירוע תקין
18. `test_event_create_end_before_start` — end < start → ValidationError

**כללים:**
- Pydantic v2 (model_config, field_validator, model_validator)
- Type hints מלאים
- הודעות שגיאה בעברית (מרוכזות ב-messages.py)
- `model_config = ConfigDict(from_attributes=True)` לתרגום מ-ORM models
- כל הטסטים רצים עם `pytest` ועוברים
```

---

## שלב 4 — שכבת Services (Business Logic Layer) ובדיקות

### מטרה:
בניית הלוגיקה העסקית — חישוב חריגות, בדיקת נעילה, Upsert logic, מנוע skip חכם, ובדיקות מקיפות.

### פרומפט:

```
אתה ממשיך בפיתוח המערכת. שלבים 0-3 (תשתית, מודלים, repositories, schemas) הושלמו. כל הטסטים הקודמים עוברים.

כעת צור את שכבת ה-Services (Business Logic) בתיקיית `app/services/` ואת הבדיקות שלהם:

**קבצים נדרשים:**

1. **user_service.py** — `UserService`:
   - Constructor מקבל `UserRepository` (DI)
   - `create_user(data: UserCreate) → UserResponse`
   - `update_user(user_id: UUID, data: UserUpdate) → UserResponse`
   - `deactivate_user(user_id: UUID) → UserResponse`
   - `get_all_active_users() → list[UserResponse]`
   - `get_user(user_id: UUID) → UserResponse`
   - `link_telegram(phone_number: str, telegram_id: str) → UserResponse` (לוגיקת אימות הבוט)

2. **week_service.py** — `WeekService`:
   - `create_week(data: WeekCreate) → WeekResponse`
   - `get_all_weeks() → list[WeekResponse]`
   - `change_week_status(week_id: UUID, new_status: WeekStatus) → WeekResponse`
   - `get_current_open_week() → WeekResponse | None`
   - `validate_week_is_open(week_id: UUID)` — זורק `WeekLockedException` אם לא פתוח

3. **submission_service.py** — `SubmissionService` (הליבה):
   - Constructor מקבל: `SubmissionRepository`, `UserRepository`, `WeekService`, `EventService` (DI)
   - `submit_constraints(user_id: UUID, data: SubmissionCreate) → SubmissionResponse`
     - מוודא שהשבוע פתוח (via WeekService)
     - מוודא שהמשתמש פעיל
     - מסנן ימים חסומים (schedule_events) — אם שומר הגיש יום שחסום, מתעלם ממנו עם log warning
     - מבצע Upsert דרך repository
     - **מחשב חריגות (deviation detection):**
       - סופר סה"כ משמרות שסומנו
       - סופר משמרות לילה (shift_type=night)
       - סופר משמרות ערב (shift_type=afternoon)
       - משווה מול `min_total_shifts`, `min_night_shifts`, `min_evening_shifts` של המשתמש
       - מסמן `has_deviation=True` אם **אחד** מהסדרים לא מתקיים
     - מחזיר response מלא כולל deviation details
   - `get_submission(user_id: UUID, week_id: UUID) → SubmissionResponse | None`
   - `get_submission_status_grid(week_id: UUID) → list[SubmissionStatusGrid]`
   - `get_missing_users(week_id: UUID) → list[UserResponse]`

4. **event_service.py** — `EventService`:
   - `create_event(data: ScheduleEventCreate) → ScheduleEventResponse`
   - `delete_event(event_id: UUID) → bool`
   - `get_user_events_for_week(user_id: UUID, week_id: UUID) → list[ScheduleEventResponse]`
   - `get_blocked_dates_for_user(user_id: UUID, start_date: date, end_date: date) → list[BlockedDateInfo]`
   - `is_user_fully_absent(user_id: UUID, start_date: date, end_date: date) → bool` (לצורך smart skip)

5. **notification_service.py** — `NotificationService`:
   - `get_users_to_notify(week_id: UUID) → tuple[list[User], list[User]]` (to_notify, skipped_auto_absence)
   - `build_submission_summary(submission: WeeklySubmission, user: User) → str` (בונה טקסט סיכום הגשה בעברית, כולל פרטי ימים ומשמרות)
   - `build_deviation_warning(user: User, deviation_details: list[DeviationDetail]) → str | None` (בונה אזהרת חריגה)

6. **export_service.py** — `ExportService` (placeholder — מימוש מלא בשלב 9):
   - `generate_excel(week_id: UUID) → bytes`

7. **settings_service.py** — `SettingsService`:
   - `get_default_shift_times() → DefaultShiftTimesResponse`
   - `update_setting(data: SystemSettingUpdate) → SystemSettingResponse`
   - `get_all_settings() → list[SystemSettingResponse]`

**בדיקות נדרשות (tests/test_services.py):**

**UserService:**
1. `test_create_user_success` — יצירת משתמש מוצלחת
2. `test_create_user_duplicate_phone` — טלפון כפול → שגיאה
3. `test_deactivate_user` — ווידוא is_active=False
4. `test_link_telegram_success` — קישור telegram_id מוצלח
5. `test_link_telegram_phone_not_found` — טלפון לא נמצא → UserNotFoundException

**WeekService:**
6. `test_create_week` — יצירת שבוע חדש
7. `test_change_status_open_to_locked` — שינוי סטטוס מוצלח
8. `test_validate_week_is_open_success` — שבוע פתוח — אין exception
9. `test_validate_week_is_open_locked` — שבוע נעול → WeekLockedException
10. `test_validate_week_is_open_published` — שבוע published → WeekLockedException

**SubmissionService (הבדיקות החשובות ביותר):**
11. `test_submit_constraints_success` — הגשה מוצלחת ללא חריגות
12. `test_submit_constraints_with_deviation` — הגשה עם חריגות (פחות משמרות מהסף)
   - שומר עם min_total_shifts=5 מגיש 3 → has_deviation=True
13. `test_submit_constraints_night_deviation` — חריגה ספציפית למשמרות לילה
14. `test_submit_constraints_no_deviation` — הגשה שעומדת בכל הסינים → has_deviation=False
15. `test_submit_to_locked_week` — הגשה לשבוע נעול → WeekLockedException
16. `test_submit_deactivated_user` — הגשה ממשתמש מושבת → UserDeactivatedException
17. `test_submit_filters_blocked_dates` — הגשה שכוללת יום חסום → היום מסונן, שאר הימים נשמרים
18. `test_upsert_overwrites_previous` — הגשה חוזרת דורסת את הקודמת
19. `test_submission_status_grid` — בדיקת טבלת סטטוסים (submitted, pending, variance, auto_absence)
20. `test_get_missing_users` — רשימת שומרים שלא הגישו

**EventService:**
21. `test_create_event` — יצירת אירוע חסימה
22. `test_get_blocked_dates` — שליפת תאריכים חסומים
23. `test_is_user_fully_absent_true` — שומר עם מילואים כל השבוע → True
24. `test_is_user_fully_absent_false` — שומר עם חופשה חלקית → False

**NotificationService:**
25. `test_get_users_to_notify_filters_absent` — מסנן שומרים עם העדרות מלאה
26. `test_build_submission_summary` — ווידוא מבנה הודעת הסיכום
27. `test_build_deviation_warning` — ווידוא אזהרת חריגה כוללת פרטים נכונים
28. `test_build_deviation_warning_none` — אין חריגה → None

**כללים:**
- כל service מקבל את ה-repositories שלו דרך constructor (Dependency Injection)
- Business logic בלבד — אין גישה ישירה ל-DB
- Error handling מקיף עם Custom Exceptions
- Logging בכל פעולה משמעותית
- כל הטקסטים בעברית מגיעים מ-messages.py
- Type hints מלאים
- Async/await
- כל הטסטים רצים עם `pytest` ועוברים
- הטסטים משתמשים ב-real test DB (לא mocks) עם fixtures מ-conftest.py
```

---

## שלב 5 — Controllers (API Routes), אימות Telegram initData ובדיקות

### מטרה:
בניית שכבת ה-API endpoints, מנגנון אימות HMAC-SHA256 של Telegram initData, ובדיקות integration.

### פרומפט:

```
אתה ממשיך בפיתוח המערכת. שלבים 0-4 (תשתית, מודלים, repositories, schemas, services) הושלמו. כל הטסטים הקודמים עוברים.

כעת צור את שכבת ה-Controllers (API Routes) בתיקיית `app/controllers/`, מנגנון האימות, ובדיקות integration:

**אימות Telegram initData (`app/utils/telegram_auth.py`):**
- פונקציה `validate_telegram_init_data(init_data: str, bot_token: str) → dict`
- מפרסרת את initData query string (urllib.parse.parse_qs)
- מחלצת את data_check_string (sorted key=value pairs, excluding hash)
- מחשבת HMAC-SHA256: secret_key = HMAC-SHA256("WebAppData", bot_token), hash = HMAC-SHA256(secret_key, data_check_string)
- משווה מול ה-hash שב-initData
- מחלצת ומפרסרת את ה-user JSON object (כולל telegram_id)
- זורקת `UserNotAuthorizedException` אם האימות נכשל
- בודקת auth_date — אם ישן מדי (>24 שעות) → exception

**עדכון `app/dependencies.py`:**
- `get_current_user(request: Request, db: AsyncSession = Depends(get_db))`:
  - מחלץ `Authorization: Bearer <initData>` מה-header
  - מפעיל `validate_telegram_init_data()`
  - מחפש user לפי telegram_id ב-DB (via UserRepository)
  - מוודא `is_active=True`
  - זורק `UserNotAuthorizedException` / `UserDeactivatedException` בהתאם
  - מחזיר User object

**Controllers נדרשים:**

1. **submission_controller.py** — prefix: `/api/submissions`
   - `GET /api/submissions/{week_id}` — שליפת הגשה קיימת (Depends: get_current_user)
   - `POST /api/submissions` — הגשה/עדכון אילוצים (Depends: get_current_user)
   - `GET /api/submissions/{week_id}/blocked-dates` — שליפת תאריכים חסומים (Depends: get_current_user)
   - `GET /api/submissions/{week_id}/defaults` — שליפת שעות ברירת מחדל + מצב השבוע (Depends: get_current_user)

2. **admin_users_controller.py** — prefix: `/api/admin/users`
   - `GET /` — רשימת כל השומרים
   - `POST /` — יצירת שומר חדש
   - `PUT /{user_id}` — עדכון שומר
   - `PATCH /{user_id}/deactivate` — השבתת שומר
   - (אימות admin: בשלב זה API key פשוט מ-header, מוגדר ב-config)

3. **admin_weeks_controller.py** — prefix: `/api/admin/weeks`
   - `GET /` — רשימת שבועות
   - `POST /` — יצירת שבוע חדש
   - `PATCH /{week_id}/status` — שינוי סטטוס שבוע
   - `GET /{week_id}/status-grid` — טבלת סטטוס הגשות

4. **admin_events_controller.py** — prefix: `/api/admin/events`
   - `GET /` — כל האירועים (עם filter אופציונלי לפי user_id)
   - `POST /` — יצירת אירוע חסימה
   - `DELETE /{event_id}` — מחיקת אירוע

5. **admin_notifications_controller.py** — prefix: `/api/admin/notifications`
   - `POST /{week_id}/send-reminder` — שליחת תזכורות (placeholder — הבוט עדיין לא מוכן, מחזיר רשימת שומרים)

6. **admin_export_controller.py** — prefix: `/api/admin/export`
   - `GET /{week_id}/excel` — ייצוא Excel (StreamingResponse)

7. **admin_settings_controller.py** — prefix: `/api/admin/settings`
   - `GET /` — כל ההגדרות
   - `PUT /` — עדכון הגדרה

**עדכון `main.py`:**
- רישום כל ה-routers עם prefixes
- CORS middleware (origins מה-config)
- Global exception handlers (מ-exceptions.py)

**בדיקות נדרשות:**

**tests/test_telegram_auth.py:**
1. `test_validate_valid_init_data` — initData תקין → מחזיר dict עם user
2. `test_validate_invalid_hash` — hash שגוי → exception
3. `test_validate_missing_hash` — initData ללא hash → exception
4. `test_validate_expired_auth_date` — auth_date ישן מ-24 שעות → exception
5. `test_validate_extracts_telegram_id` — ווידוא שה-telegram_id מחולץ נכון
6. `test_validate_with_different_bot_token` — token שגוי → exception

**tests/test_api_submissions.py:**
7. `test_get_submission_success` — שליפת הגשה קיימת → 200
8. `test_get_submission_not_found` — אין הגשה → 200 עם null
9. `test_post_submission_success` — הגשה מוצלחת → 201
10. `test_post_submission_locked_week` — הגשה לשבוע נעול → 403
11. `test_post_submission_unauthorized` — ללא auth header → 401
12. `test_post_submission_deactivated_user` — משתמש מושבת → 403
13. `test_get_blocked_dates` — שליפת תאריכים חסומים → 200 + רשימה
14. `test_get_defaults` — שליפת ברירות מחדל → 200 + שעות

**tests/test_api_admin.py:**
15. `test_admin_list_users` — רשימת שומרים → 200
16. `test_admin_create_user` — יצירת שומר → 201
17. `test_admin_update_user` — עדכון שומר → 200
18. `test_admin_deactivate_user` — השבתה → 200
19. `test_admin_create_week` — יצירת שבוע → 201
20. `test_admin_change_week_status` — שינוי סטטוס → 200
21. `test_admin_status_grid` — טבלת סטטוס → 200
22. `test_admin_create_event` — יצירת אירוע → 201
23. `test_admin_delete_event` — מחיקת אירוע → 200
24. `test_admin_get_settings` — הגדרות → 200
25. `test_admin_update_setting` — עדכון הגדרה → 200

**כללים:**
- Controllers דקים — מעבירים ל-Services
- Dependency Injection (Depends) לכל service ו-repository
- Response models מוגדרים ב-schemas
- HTTP status codes מתאימים (200, 201, 403, 404, 409)
- Logging בכל endpoint
- Type hints מלאים
- הבדיקות משתמשות ב-httpx.AsyncClient + test_app מ-conftest
- Override ל-dependencies בטסטים (mock user, mock session)
- כל הטסטים רצים עם `pytest` ועוברים
```

---

## שלב 6 — Telegram Bot (aiogram) ובדיקות

### מטרה:
בניית בוט הטלגרם — אימות משתמשים, התראות אוטומטיות, תזכורות, סיכום הגשה, Cron Jobs, ובדיקות.

### פרומפט:

```
אתה ממשיך בפיתוח המערכת. שלבים 0-5 (תשתית, מודלים, repositories, schemas, services, controllers) הושלמו. כל הטסטים הקודמים עוברים.

כעת צור את בוט הטלגרם בתיקיית `app/bot/` ואת הבדיקות:

**מבנה:**
```
app/bot/
├── __init__.py
├── bot_instance.py         # Bot + Dispatcher initialization
├── handlers/
│   ├── __init__.py
│   ├── start_handler.py    # /start command + contact sharing
│   ├── submit_handler.py   # /submit_anyway command
│   └── fallback_handler.py # Generic message handler (lockout refusal)
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
└── notifications.py         # Send summary, reminder, etc.
```

**דרישות מפורטות:**

1. **bot_instance.py**: 
   - אתחול Bot ו-Dispatcher של aiogram v3
   - קריאת token מ-config (Settings)
   - רישום כל ה-handlers
   - פונקציית `start_bot()` ו-`stop_bot()` לאינטגרציה עם FastAPI lifespan

2. **start_handler.py** — תהליך אימות (Onboarding):
   - `/start` → שליחת הודעה בעברית (Messages.BOT_WELCOME) + contact keyboard
   - קבלת contact → שליפת phone_number → נרמול (הסרת +972, רווחים) → בדיקה מול DB
   - אם נמצא: שמירת telegram_id + הודעת Messages.BOT_AUTH_SUCCESS
   - אם לא נמצא: הודעת Messages.BOT_AUTH_FAIL

3. **submit_handler.py** — `/submit_anyway`:
   - בדיקה שהמשתמש מאומת (יש telegram_id ב-DB)
   - שליחת Messages.BOT_SUBMIT_ANYWAY + webapp inline keyboard
   - אם לא מאומת → Messages.BOT_AUTH_FAIL

4. **fallback_handler.py**:
   - אם השבוע locked/published → Messages.BOT_LOCKOUT
   - אחרת → הודעת ברירת מחדל עם webapp keyboard

5. **contact_keyboard.py**: `ReplyKeyboardMarkup` עם `KeyboardButton(text=Messages.BOT_SHARE_CONTACT_BUTTON, request_contact=True)`, one_time_keyboard=True

6. **webapp_keyboard.py**: `InlineKeyboardMarkup` עם `WebAppInfo(url=config.WEBAPP_URL)`, button text מ-Messages

7. **auth_middleware.py**: Middleware של aiogram שבודק:
   - המשתמש קיים ב-DB לפי telegram_id
   - is_active=True
   - מוסיף user object ל-handler data

8. **weekly_opener.py** — Cron Job:
   - פונקציה async `run_weekly_opening()`
   - נרשמת עם APScheduler או asyncio כ-periodic task
   - יום ושעה מוגדרים ב-config (CRON_WEEKLY_OPEN_DAY, CRON_WEEKLY_OPEN_HOUR)
   - שולפת שבוע פתוח נוכחי
   - שולפת רשימת שומרים פעילים
   - **Smart Skip Filter:** לכל שומר — בודקת via EventService.is_user_fully_absent(). אם True → log Auto-Absence, skip
   - לשאר → שולחת Messages.BOT_WEEK_OPEN + webapp keyboard
   - **Logging מפורט:** מי קיבל, מי דולג, שגיאות שליחה (כולל TelegramBadRequest if bot blocked)
   - מחזירה stats: sent_count, skipped_count, failed_count

9. **notifications.py** — פונקציות שליחה:
   - `send_submission_summary(bot: Bot, telegram_id: str, summary_text: str) → bool`
   - `send_reminder(bot: Bot, telegram_id: str) → bool` — Messages.BOT_REMINDER + webapp keyboard
   - `send_weekly_opening(bot: Bot, telegram_id: str) → bool` — Messages.BOT_WEEK_OPEN + webapp keyboard
   - כל פונקציה: try/except, logging, מחזירה True/False

10. **אינטגרציה:**
    - עדכון `app/main.py` — הוספת bot startup/shutdown ב-lifespan
    - עדכון `submission_service.py` — אחרי הגשה מוצלחת, קריאה ל-send_submission_summary
    - עדכון `admin_notifications_controller.py` — מימוש שליחת תזכורות בפועל

**בדיקות נדרשות (tests/test_bot.py):**

1. `test_start_handler_sends_welcome` — /start שולח Messages.BOT_WELCOME + contact keyboard
2. `test_contact_handler_valid_phone` — שיתוף contact עם טלפון קיים → auth success + telegram_id saved
3. `test_contact_handler_invalid_phone` — טלפון לא קיים ב-DB → auth fail message
4. `test_contact_handler_normalizes_phone` — נרמול +972 → 05... לפני חיפוש
5. `test_submit_anyway_authenticated` — /submit_anyway ממשתמש מאומת → webapp keyboard
6. `test_submit_anyway_unauthenticated` — /submit_anyway ממשתמש לא מאומת → auth fail
7. `test_fallback_locked_week` — הודעה כשהשבוע נעול → lockout message
8. `test_auth_middleware_blocks_inactive` — middleware חוסם משתמש מושבת

**tests/test_cron.py:**
9. `test_weekly_opener_sends_to_active` — שולח הודעה לשומרים פעילים
10. `test_weekly_opener_skips_fully_absent` — מדלג על שומר עם מילואים כל השבוע
11. `test_weekly_opener_handles_blocked_bot` — מטפל בשגיאה כש-bot חסום (TelegramBadRequest)
12. `test_weekly_opener_no_open_week` — אין שבוע פתוח → log warning, no messages sent
13. `test_weekly_opener_returns_stats` — מחזיר stats נכונים

**tests/test_notifications.py:**
14. `test_send_submission_summary_success` — שליחת סיכום מוצלחת
15. `test_send_submission_summary_with_deviation` — סיכום כולל אזהרת חריגה
16. `test_send_reminder_success` — שליחת תזכורת מוצלחת
17. `test_send_reminder_bot_blocked` — bot חסום → False + log

**כללים:**
- כל הטקסטים מ-messages.py — אפס hard coding
- Error handling: אם שומר חסם את הבוט — log + skip (לא crash)
- Logging מפורט בכל שלב
- Async/await בכל מקום
- Bot Token מה-config
- הטסטים משתמשים ב-mock של aiogram Bot (לא שולחים הודעות אמיתיות)
- כל הטסטים רצים עם `pytest` ועוברים
```

---

## שלב 7 — Telegram Web App (Frontend — טופס הגשת אילוצים) ובדיקות

### מטרה:
בניית ה-SPA שרץ בתוך Telegram, עם טופס הגשת אילוצים שבועי, תמיכה ב-Upsert, חסימות, Read-Only mode, ובדיקות קומפוננטות.

### פרומפט:

```
אתה ממשיך בפיתוח המערכת. שלבים 0-6 (Backend מלא + Bot) הושלמו. כל הטסטים הקודמים עוברים.

כעת צור את ה-Telegram Web App — אפליקציית Frontend (SPA) שרצה בתוך Telegram:

**טכנולוגיה:** React 18 עם Vite, כולל Vitest + React Testing Library לבדיקות

**מבנה:**
```
frontend/webapp/
├── index.html
├── vite.config.js
├── package.json
├── .env.example
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   ├── api/
│   │   └── apiClient.js        # Fetch wrapper with Telegram initData auth
│   ├── components/
│   │   ├── WeekForm.jsx         # Main form component
│   │   ├── DayCard.jsx          # Single day availability card
│   │   ├── ShiftCheckbox.jsx    # Shift toggle with time inputs
│   │   ├── BlockedDay.jsx       # Disabled day (vacation/military)
│   │   ├── LockBanner.jsx       # Read-only banner
│   │   ├── NotesField.jsx       # General notes textarea
│   │   ├── LoadingSpinner.jsx   # Loading state
│   │   └── ErrorMessage.jsx     # Error display
│   ├── hooks/
│   │   ├── useSubmission.js     # Data fetching & submission logic
│   │   └── useTelegram.js       # Telegram WebApp SDK integration
│   ├── utils/
│   │   └── messages.js          # Frontend Hebrew texts
│   └── styles/
│       └── main.css             # Mobile-first RTL responsive design
├── __tests__/
│   ├── setup.js                 # Test setup (jsdom, mocks)
│   ├── WeekForm.test.jsx        # Main form tests
│   ├── DayCard.test.jsx         # Day card tests
│   ├── ShiftCheckbox.test.jsx   # Shift checkbox tests
│   ├── BlockedDay.test.jsx      # Blocked day tests
│   ├── LockBanner.test.jsx      # Lock banner tests
│   ├── useSubmission.test.js    # Hook tests
│   └── apiClient.test.js        # API client tests
```

**דרישות מפורטות:**

1. **Telegram SDK Integration (`useTelegram.js`):**
   - אתחול `window.Telegram.WebApp`
   - חילוץ `initData` string
   - `initDataUnsafe` לקריאת user info
   - שימוש ב-`MainButton` של Telegram (כפתור "שלח" native)
   - `themeParams` לצבעי UI
   - `close()` אחרי הגשה מוצלחת

2. **API Client (`apiClient.js`):**
   - כל בקשה שולחת `Authorization: Bearer <initData>` ב-header
   - Base URL מ-`import.meta.env.VITE_API_URL`
   - Error handling גלובלי: 403 → הודעת נעילה, 401 → הודעת אימות, 409 → conflict
   - Retry logic (אופציונלי)

3. **זרימת טעינה (useSubmission hook):**
   - בטעינה: שלוש קריאות API במקביל (Promise.all):
     - `GET /api/submissions/{week_id}` — הגשה קיימת (prefill)
     - `GET /api/submissions/{week_id}/blocked-dates` — תאריכים חסומים
     - `GET /api/submissions/{week_id}/defaults` — שעות ברירת מחדל + סטטוס שבוע
   - States: loading, error, data, blockedDates, defaults, isReadOnly
   - `submitForm(formData)` — שליחת הטופס

4. **ארכיטקטורת הטופס (WeekForm):**
   - רשימה כרונולוגית של 7 ימים (ראשון עד שבת)
   - לכל יום: DayCard component
   - שדה הערות (NotesField) בתחתית

5. **DayCard:**
   - Toggle "זמין" / "לא זמין"
   - כשזמין: ShiftCheckbox × 3 (בוקר, צהריים, לילה)
   - שם היום בעברית + תאריך

6. **ShiftCheckbox:**
   - Checkbox עם label (Messages.LABEL_MORNING / AFTERNOON / NIGHT)
   - כשמסומן: שדות input type="time" — "משעה" ו"עד שעה"
   - ערכי ברירת מחדל מ-defaults

7. **BlockedDay:**
   - יום חסום → מוצג כ-disabled, אפור
   - Label: "חסום — {סוג_אירוע}" (מ-messages.js)
   - לא ניתן ללחוץ

8. **LockBanner:**
   - כשהשבוע locked/published → באנר קבוע בראש (מ-messages.js)
   - כל הטופס disabled

9. **שליחה:**
   - JSON payload: { week_id, general_notes, days: [{ date, is_available, shifts: [{ shift_type, start_time, end_time }] }] }
   - POST → Loading state → Success: Telegram.WebApp.close() / Error: ErrorMessage

10. **עיצוב:**
    - RTL (direction: rtl, text-align: right)
    - Mobile-first
    - Telegram Theme colors (var(--tg-theme-bg-color) etc.)
    - נגיש
    - כל טקסט מ-messages.js

**בדיקות נדרשות (__tests__/):**

1. `WeekForm.test.jsx`:
   - renders 7 day cards
   - renders notes field
   - renders lock banner when read-only
   - hides submit button when read-only

2. `DayCard.test.jsx`:
   - toggles between available/unavailable
   - shows shift checkboxes when available
   - hides shift checkboxes when unavailable
   - displays day name in Hebrew

3. `ShiftCheckbox.test.jsx`:
   - shows time inputs when checked
   - hides time inputs when unchecked
   - initializes with default times
   - allows time editing

4. `BlockedDay.test.jsx`:
   - renders as disabled
   - shows correct event type label
   - click does nothing

5. `LockBanner.test.jsx`:
   - renders with correct message
   - visible when locked
   - hidden when open

6. `useSubmission.test.js`:
   - fetches data on mount
   - sets loading state
   - handles API errors
   - submits form data correctly

7. `apiClient.test.js`:
   - adds auth header to requests
   - handles 401 errors
   - handles 403 errors
   - uses correct base URL

**כללים:**
- אפס hard coding של טקסטים — הכל מ-messages.js
- אפס hard coding של URLs — הכל מ-env
- Error handling מלא בצד לקוח
- Loading states בכל קריאת API
- כל הטסטים רצים עם `npm test` ועוברים
```

---

## שלב 8 — Admin Dashboard (Frontend) ובדיקות

### מטרה:
בניית דאשבורד ניהול עבור קצין הביטחון — ניהול שומרים, שבועות, אירועי חסימה, מעקב הגשות, שליחת תזכורות, ובדיקות.

### פרומפט:

```
אתה ממשיך בפיתוח המערכת. שלבים 0-7 (Backend + Bot + Web App) הושלמו. כל הטסטים הקודמים עוברים.

כעת צור את ה-Admin Dashboard — ממשק ניהול (SPA) עם בדיקות:

**טכנולוגיה:** React 18 עם Vite + React Router, כולל Vitest + React Testing Library

**מבנה:**
```
frontend/admin/
├── index.html
├── vite.config.js
├── package.json
├── .env.example
├── src/
│   ├── main.jsx
│   ├── App.jsx                   # Router setup
│   ├── api/
│   │   └── adminApiClient.js     # Fetch wrapper with admin auth
│   ├── pages/
│   │   ├── GuardsPage.jsx        # CRUD שומרים
│   │   ├── WeeksPage.jsx         # ניהול שבועות
│   │   ├── EventsPage.jsx        # אירועי חסימה
│   │   ├── SubmissionsPage.jsx   # מעקב הגשות + תזכורות
│   │   ├── SettingsPage.jsx      # הגדרות מערכת
│   │   └── ExportPage.jsx        # ייצוא Excel
│   ├── components/
│   │   ├── GuardForm.jsx         # טופס יצירת/עריכת שומר
│   │   ├── GuardTable.jsx        # טבלת שומרים
│   │   ├── WeekStatusControl.jsx # שינוי סטטוס שבוע
│   │   ├── StatusGrid.jsx        # טבלת סטטוס הגשות
│   │   ├── EventForm.jsx         # טופס אירוע חסימה
│   │   ├── ConfirmDialog.jsx     # דיאלוג אישור לפני פעולות הרסניות
│   │   └── Navbar.jsx            # ניווט עליון
│   ├── hooks/
│   │   ├── useGuards.js
│   │   ├── useWeeks.js
│   │   ├── useSubmissions.js
│   │   └── useSettings.js
│   ├── utils/
│   │   └── messages.js           # טקסטים בעברית
│   └── styles/
│       └── admin.css
├── __tests__/
│   ├── setup.js
│   ├── GuardsPage.test.jsx
│   ├── WeeksPage.test.jsx
│   ├── SubmissionsPage.test.jsx
│   ├── StatusGrid.test.jsx
│   ├── GuardForm.test.jsx
│   └── ConfirmDialog.test.jsx
```

**דפים נדרשים:**

1. **GuardsPage — ניהול שומרים:**
   - טבלה: שם, טלפון, תפקיד, סטטוס (פעיל/מושבת), Telegram מחובר (✅/❌)
   - כפתור "הוסף שומר" → GuardForm (modal)
   - עריכת שומר → GuardForm (modal, prefilled)
   - הגדרת סף מינימום: כללי, לילה, ערב
   - כפתור "השבת" עם ConfirmDialog

2. **WeeksPage — ניהול שבועות:**
   - רשימת שבועות (תאריכים, סטטוס badge)
   - יצירת שבוע (date pickers)
   - **WeekStatusControl:** כפתורים Open → Locked → Published, עם ConfirmDialog לפני שינוי

3. **EventsPage — אירועי חסימה:**
   - Dropdown לבחירת שומר
   - EventForm: סוג + תאריכים
   - רשימת אירועים + כפתור מחיקה עם ConfirmDialog

4. **SubmissionsPage — מעקב הגשות (הדף המרכזי):**
   - Dropdown לבחירת שבוע
   - **StatusGrid:** טבלה — שומר | סטטוס | תאריך הגשה | חריגה
   - סטטוסים צבעוניים: "הוגש ✅", "הוגש עם חריגה ⚠️", "ממתין להגשה 🔴", "העדרות אוטומטית 📋"
   - Counter: "הגישו X מתוך Y"
   - כפתור **"שלח תזכורת"** (שולח רק למי שממתין) + ConfirmDialog + feedback

5. **SettingsPage:** עריכת שעות ברירת מחדל (6 שדות time)

6. **ExportPage:** בחירת שבוע + כפתור "הורד Excel" (download trigger)

**בדיקות נדרשות (__tests__/):**

1. `GuardsPage.test.jsx`:
   - renders guard table with data
   - opens form on "add" click
   - submits new guard successfully
   - deactivate button shows confirm dialog
   - displays telegram connection status

2. `WeeksPage.test.jsx`:
   - renders weeks list
   - creates new week
   - status change shows confirm dialog
   - status badges render correctly

3. `SubmissionsPage.test.jsx`:
   - renders status grid for selected week
   - shows correct status icons
   - "send reminder" button triggers API call
   - displays counter (X of Y)

4. `StatusGrid.test.jsx`:
   - renders all statuses correctly
   - highlights deviations
   - sorts by status

5. `GuardForm.test.jsx`:
   - validates required fields
   - validates phone format
   - submits valid data
   - shows errors on invalid input

6. `ConfirmDialog.test.jsx`:
   - shows correct message
   - calls onConfirm on confirm
   - calls onCancel on cancel
   - closes on backdrop click

**כללים:**
- RTL layout
- Mobile responsive
- כל הטקסטים מ-messages.js
- Error handling + loading states
- ConfirmDialog לפני כל פעולה הרסנית
- כל הטסטים רצים עם `npm test` ועוברים
```

---

## שלב 9 — ייצוא Excel (openpyxl) ובדיקות

### מטרה:
מימוש מנוע ייצוא ה-Excel עם openpyxl, כולל עיצוב, headers, מבנה מטריצה, ובדיקות.

### פרומפט:

```
אתה ממשיך בפיתוח המערכת. שלבים 0-8 הושלמו. כל הטסטים הקודמים עוברים.

כעת מלא את מימוש ה-ExportService עם openpyxl ואת הבדיקות:

**מימוש `app/services/export_service.py`:**

1. **מבנה הגיליון (Matrix Layout):**
   - **שורה 1:** כותרת ראשית: "דוח משמרות — {start_date} עד {end_date}"
   - **שורה 2:** כותרות משנה מקובצות:
     - עמודה A: "שם"
     - עמודה B: "טלפון"
     - לכל יום (ראשון-שבת): 3 עמודות (בוקר | צהריים | לילה), עם header של שם היום + תאריך
     - עמודה אחרונה-2: "הערות"
     - עמודה אחרונה-1: "סף מינימום"
     - עמודה אחרונה: "חריגה"
   - **שורות 3+:** שומרים
     - תוכן תא: שעות ("07:00-15:00") / "לא זמין" / "חסום" / ריק
     - עמודת הערות: general_notes
     - עמודת סף: "כללי: X, לילה: Y, ערב: Z"
     - עמודת חריגה: "✓" / "⚠ חריגה"

2. **עיצוב:**
   - Headers: רקע כחול כהה, טקסט לבן, bold
   - שמות ימים: רקע כחול בהיר
   - תאי חריגה: רקע אדום בהיר, טקסט אדום
   - תאי "חסום": רקע אפור, italic
   - Borders דקים בכל התאים
   - Auto-fit column widths (approximation)
   - Freeze panes: שתי שורות ראשונות + שתי עמודות ראשונות
   - RTL: sheet.sheet_view.rightToLeft = True
   - Merge cells לכותרות ימים (כל יום = 3 עמודות)

3. **שם הקובץ:** `shifts_report_{start_date}_{end_date}.xlsx`

4. **ה-endpoint:** `StreamingResponse` with proper content-type and content-disposition headers

**בדיקות נדרשות (tests/test_export.py):**

1. `test_generate_excel_returns_bytes` — הפונקציה מחזירה bytes תקינים
2. `test_excel_opens_as_workbook` — ה-bytes נפתחים כ-openpyxl Workbook
3. `test_excel_has_correct_headers` — כותרות נכונות (שם, טלפון, ימים)
4. `test_excel_has_correct_row_count` — מספר שורות = מספר שומרים + headers
5. `test_excel_cell_content_available` — תא עם שעות זמינות מכיל format נכון
6. `test_excel_cell_content_unavailable` — תא "לא זמין"
7. `test_excel_cell_content_blocked` — תא "חסום"
8. `test_excel_deviation_marking` — שומר עם חריגה מסומן
9. `test_excel_rtl_enabled` — RTL מופעל
10. `test_excel_freeze_panes` — freeze panes מוגדר
11. `test_excel_empty_week` — שבוע ללא הגשות → workbook עם headers בלבד
12. `test_excel_filename_format` — שם הקובץ בפורמט הנכון

**כללים:**
- כל הטקסטים (כותרות, labels) מ-messages.py
- Error handling אם אין הגשות
- Logging
- כל הטסטים רצים עם `pytest` ועוברים
```

---

## שלב 10 — Dockerization ובדיקות E2E

### מטרה:
קונטיינריזציה של כל המערכת, docker-compose להרצה מקומית, ובדיקות End-to-End.

### פרומפט:

```
אתה ממשיך בפיתוח המערכת. שלבים 0-9 הושלמו. כל הטסטים הקודמים עוברים.

כעת צור את תשתית ה-Docker ובדיקות E2E:

**Docker:**

1. **`backend/Dockerfile`:**
   - Multi-stage build
   - Base: python:3.11-slim
   - Install requirements
   - Copy app
   - Run with uvicorn
   - Health check endpoint

2. **`frontend/webapp/Dockerfile`:**
   - Stage 1: node:18-alpine, npm install + build
   - Stage 2: nginx:alpine, copy build output
   - Custom nginx.conf (SPA routing)

3. **`frontend/admin/Dockerfile`:**
   - כנ"ל

4. **`docker-compose.yml`:**
   ```yaml
   services:
     db:
       image: postgres:15-alpine
       volumes: [postgres_data:/var/lib/postgresql/data]
       environment: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
       healthcheck: pg_isready

     backend:
       build: ./backend
       ports: ["8000:8000"]
       depends_on: db (healthy)
       env_file: .env
       command: >
         sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"

     webapp:
       build: ./frontend/webapp
       ports: ["3000:80"]

     admin:
       build: ./frontend/admin
       ports: ["3001:80"]

   volumes:
     postgres_data:
   ```

5. **`docker-compose.dev.yml`:** Override עם:
   - Volume mounts לקוד (hot reload)
   - `uvicorn --reload`
   - npm dev servers במקום nginx

6. **`.env` root file:** כל המשתנים (DB, tokens, URLs)

7. **`Makefile`:** 
   - `make up` — docker-compose up
   - `make down` — docker-compose down
   - `make dev` — docker-compose -f ... up (dev mode)
   - `make test` — run all tests
   - `make migrate` — alembic upgrade head
   - `make logs` — docker-compose logs -f

**בדיקות E2E (tests/test_e2e.py):**

1. `test_health_check` — GET /health → 200
2. `test_full_guard_lifecycle` — create user → link telegram → submit → verify
3. `test_admin_week_lifecycle` — create week → open → lock → verify submissions blocked
4. `test_submission_upsert_flow` — submit → re-submit → verify only latest
5. `test_blocked_date_respected` — create event → submit including blocked date → blocked date filtered
6. `test_deviation_detection_e2e` — create user with thresholds → submit below threshold → verify deviation
7. `test_export_excel_e2e` — create data → export → verify file is valid xlsx
8. `test_status_grid_accuracy` — create mixed submissions → verify grid shows correct statuses

**כללים:**
- Docker images מינימליים (alpine/slim)
- Health checks
- Non-root user ב-containers
- .dockerignore files
- Environment variables מ-.env
- כל הטסטים רצים עם `pytest` / `npm test` ועוברים
- Makefile לנוחות
```

---

## סיכום שלבים

| # | שלב | תיאור | בדיקות | תלויות |
|---|------|--------|--------|---------|
| 0 | תשתית | מבנה פרויקט, config, logging, messages, exceptions, test infra | config, messages, constants, exceptions | — |
| 1 | מודלים | SQLAlchemy ORM models + Alembic | models CRUD, constraints, relationships, cascades | שלב 0 |
| 2 | Repositories | Data Access Layer | 24 טסטים: CRUD, queries, edge cases | שלב 1 |
| 3 | Schemas | Pydantic v2 validation | 18 טסטים: valid/invalid inputs, validators | שלב 0 |
| 4 | Services | Business Logic | 28 טסטים: deviation, upsert, locking, smart skip | שלבים 2, 3 |
| 5 | Controllers | API Routes + Telegram Auth | 25 טסטים: endpoints, auth, status codes | שלב 4 |
| 6 | Bot | Telegram Bot (aiogram) + Cron | 17 טסטים: handlers, cron, notifications | שלבים 4, 5 |
| 7 | Web App | Telegram Web App (React) | 7 test suites: components, hooks, API | שלב 5 |
| 8 | Dashboard | Admin Dashboard (React) | 6 test suites: pages, components, forms | שלב 5 |
| 9 | Excel | Export Engine (openpyxl) | 12 טסטים: structure, content, styling | שלב 4 |
| 10 | Docker & E2E | Containerization + E2E Tests | 8 טסטים: full lifecycle flows | כל השלבים |

---

> **הערה חשובה:** כל פרומפט מתחיל בציון "כל הטסטים הקודמים עוברים" — זה מבטיח שהקוד החדש לא שובר את הקיים. כל שלב הוא יחידה סגורה עם הבדיקות שלה.
