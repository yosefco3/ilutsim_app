# Step 1 — Database Models (SQLAlchemy ORM) & Alembic Migrations

## Context
You are continuing development of the Micro-SaaS security guard shift constraint management system. **Step 0 (infrastructure, config, logging, messages, test setup) is complete. All previous tests pass.**

**Important:** All user-facing text is in Hebrew (centralized in `messages.py`). Code comments in English.

## Objective
Create all SQLAlchemy ORM models per the database schema specification, configure Alembic for async migrations, create the initial migration with seed data, and write comprehensive model tests.

## Models Required (in `app/models/`)

### 1. `base.py` — Shared Base Class
- `BaseModel` class using SQLAlchemy 2.0 declarative style (`DeclarativeBase` or `MappedAsDataclass`)
- Common columns:
  - `id`: `Mapped[uuid.UUID]` — primary key, default `uuid.uuid4`
  - `created_at`: `Mapped[datetime]` — server default `func.now()`
  - `updated_at`: `Mapped[datetime]` — server default `func.now()`, onupdate `func.now()`
- Auto-generate `__tablename__` from class name (e.g., `User` → `users`)

### 2. `user.py` — Table: `users`
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| phone_number | String(20) | unique, not null | Guard's phone number |
| telegram_id | String(50) | unique, nullable | Telegram user ID, set after contact sharing |
| full_name | String(100) | not null | Guard's display name |
| role | Enum(UserRole) | not null | guard / shift_lead / scanner |
| is_active | Boolean | default True | Soft delete flag |
| exemptions_notes | Text | nullable | Free-text permanent exemptions |
| min_total_shifts | Integer | default 0 | Minimum total shifts per week |
| min_night_shifts | Integer | default 0 | Minimum night shifts per week |
| min_evening_shifts | Integer | default 0 | Minimum evening shifts per week |

**Relationships:**
- `schedule_events` → one-to-many with ScheduleEvent
- `weekly_submissions` → one-to-many with WeeklySubmission

**Indexes:** `phone_number`, `telegram_id`

### 3. `schedule_week.py` — Table: `schedule_weeks`
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| start_date | Date | not null | Week start (typically Sunday) |
| end_date | Date | not null | Week end (typically Saturday) |
| status | Enum(WeekStatus) | not null, default 'open' | open / locked / published |

**Relationships:**
- `weekly_submissions` → one-to-many with WeeklySubmission

### 4. `schedule_event.py` — Table: `schedule_events`
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | UUID | FK → users.id, not null | Link to guard |
| event_type | Enum(EventType) | not null | vacation / military_reserve / firearms_training |
| start_date | Date | not null | Blockout start |
| end_date | Date | not null | Blockout end |

**Relationships:**
- `user` → many-to-one with User

### 5. `weekly_submission.py` — Table: `weekly_submissions`
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | UUID | FK → users.id, not null | Submitting guard |
| week_id | UUID | FK → schedule_weeks.id, not null | Target week |
| general_notes | Text | nullable | Free-form remarks |
| has_deviation | Boolean | default False | Flag: violates baseline thresholds |
| submitted_at | DateTime | not null, auto-set | Timestamp of submission |

**Constraints:**
- `UniqueConstraint('user_id', 'week_id')` — prevent duplicate submissions

**Relationships:**
- `user` → many-to-one with User
- `week` → many-to-one with ScheduleWeek
- `daily_statuses` → one-to-many with DailyStatus (cascade all, delete-orphan)

### 6. `daily_status.py` — Table: `daily_statuses`
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| submission_id | UUID | FK → weekly_submissions.id, ondelete CASCADE | Parent submission |
| date | Date | not null | Specific calendar day |
| is_available | Boolean | not null | Available (True) or unavailable (False) |

**Relationships:**
- `submission` → many-to-one with WeeklySubmission
- `shift_windows` → one-to-many with ShiftWindow (cascade all, delete-orphan)

### 7. `shift_window.py` — Table: `shift_windows`
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| daily_status_id | UUID | FK → daily_statuses.id, ondelete CASCADE | Parent day record |
| shift_type | Enum(ShiftType) | not null | morning / afternoon / night |
| start_time | Time | not null | Shift start time |
| end_time | Time | not null | Shift end time |

### 8. `admin.py` — Table: `admins`
**Note: This model does NOT inherit from BaseModel** (uses auto-increment integer PK for simplicity).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | primary key, autoincrement | Admin user ID |
| email | String(255) | unique, not null | Admin email (used for login) |
| password_hash | String(255) | not null | Bcrypt hashed password |
| full_name | String(100) | not null | Display name |
| role | Enum(AdminRole) | not null, default 'admin' | super_admin / admin / viewer |
| is_active | Boolean | default True | Can be deactivated |
| created_at | DateTime | server default now() | |
| updated_at | DateTime | onupdate now() | |

**Indexes:** `email` (unique)

### 9. `system_setting.py` — Table: `system_settings`
**Note: This model does NOT inherit from BaseModel** (PK is string, not UUID).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| setting_key | String(100) | primary key | e.g., "default_morning_start" |
| setting_value | String(255) | not null | e.g., "07:00" |
| description | String(500) | nullable | Explanation of the setting |
| created_at | DateTime | server default now() | |
| updated_at | DateTime | onupdate now() | |

### 10. `__init__.py`
Import ALL models so Alembic's `autogenerate` detects them:
```python
from app.models.base import BaseModel
from app.models.user import User
from app.models.schedule_week import ScheduleWeek
from app.models.schedule_event import ScheduleEvent
from app.models.weekly_submission import WeeklySubmission
from app.models.daily_status import DailyStatus
from app.models.shift_window import ShiftWindow
from app.models.admin import Admin
from app.models.system_setting import SystemSetting
```

## Alembic Configuration

### `alembic.ini`
- Set `sqlalchemy.url` to empty (will be overridden by env.py)

### `alembic/env.py`
- Import `Settings` from `app.config`
- Read `DATABASE_URL_SYNC` from settings for migration URL
- Import `BaseModel.metadata` as `target_metadata`
- Configure for both online and offline migrations

### Initial Migration: `initial_schema`
- Generate with `alembic revision --autogenerate -m "initial_schema"`
- Add seed data in the `upgrade()` function:
```python
# Seed default system settings
op.bulk_insert(system_settings_table, [
    {"setting_key": "default_morning_start", "setting_value": "07:00", "description": "Default morning shift start time"},
    {"setting_key": "default_morning_end", "setting_value": "15:00", "description": "Default morning shift end time"},
    {"setting_key": "default_afternoon_start", "setting_value": "15:00", "description": "Default afternoon shift start time"},
    {"setting_key": "default_afternoon_end", "setting_value": "23:00", "description": "Default afternoon shift end time"},
    {"setting_key": "default_night_start", "setting_value": "23:00", "description": "Default night shift start time"},
    {"setting_key": "default_night_end", "setting_value": "07:00", "description": "Default night shift end time"},
])

# Seed default super admin (password: "changeme" — must be changed on first login)
# Use bcrypt hash of "changeme"
import bcrypt
password_hash = bcrypt.hashpw(b"changeme", bcrypt.gensalt()).decode("utf-8")
op.bulk_insert(admins_table, [
    {"email": "admin@ilutzim.com", "password_hash": password_hash, "full_name": "System Admin", "role": "super_admin", "is_active": True},
])
```

## Tests Required (`tests/test_models.py`)

### User Model
1. `test_create_user` — Create a user with all fields, save to DB, verify all fields are stored correctly
2. `test_user_unique_phone` — Create two users with the same phone_number → `IntegrityError`
3. `test_user_unique_telegram_id` — Create two users with the same telegram_id → `IntegrityError`
4. `test_user_default_values` — Create user with minimal fields, verify defaults: `is_active=True`, `min_total_shifts=0`, `min_night_shifts=0`, `min_evening_shifts=0`

### ScheduleWeek Model
5. `test_create_schedule_week` — Create a week, verify `status` defaults to `WeekStatus.open`

### ScheduleEvent Model
6. `test_create_schedule_event` — Create an event linked to a user, verify the `user` relationship works

### WeeklySubmission Model
7. `test_create_weekly_submission` — Create a submission linked to user and week
8. `test_duplicate_submission_constraint` — Create two submissions for the same user+week → `IntegrityError`

### Cascade Behavior
9. `test_cascade_delete_submission` — Delete a submission, verify its `daily_statuses` and their `shift_windows` are also deleted
10. `test_create_full_submission_chain` — Create: submission → daily_status → shift_window, navigate relationships in both directions

### SystemSetting Model
11. `test_system_setting_crud` — Create, read, and update a system setting

### Auto-generated Fields
12. `test_uuid_auto_generation` — Create a model, verify `id` is a valid UUID (not None)
13. `test_timestamps_auto_set` — Create a model, verify `created_at` and `updated_at` are set automatically

## Rules
- All models use SQLAlchemy 2.0 style (`Mapped`, `mapped_column`)
- UUID as primary key everywhere
- Proper indexes on frequently queried fields
- Cascade delete: submission → daily_statuses → shift_windows
- Full type hints
- All tests must pass with `pytest`
- Code comments in English
