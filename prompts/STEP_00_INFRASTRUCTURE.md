# Step 0 — Project Infrastructure, Configuration, Logging & Test Setup

## Context
You are a senior software architect and expert Full-Stack developer. You are building a Micro-SaaS system for managing security guard shift constraints. **Important:** The entire application UI, bot messages, and user-facing text must be in **Hebrew only**. Code comments should be in **English**.

## Objective
Create the foundational project structure for the backend: folder layout, configuration management, structured logging, centralized Hebrew messages file, enums/constants, custom exceptions with global handlers, dependency injection setup, and test infrastructure.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app factory + lifespan
│   ├── config.py                # Settings class (Pydantic BaseSettings, reads .env)
│   ├── database.py              # Async engine + session factory
│   ├── logging_config.py        # Structured logging setup (JSON format)
│   ├── messages.py              # ALL Hebrew texts centralized here
│   ├── constants.py             # Enums, default values, shift types
│   ├── dependencies.py          # Dependency injection (DB session, current user, etc.)
│   ├── exceptions.py            # Custom exception classes + global handlers
│   ├── controllers/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   ├── repositories/
│   │   └── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   ├── bot/
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures: test DB, async session, test client
│   ├── test_config.py
│   ├── test_messages.py
│   ├── test_constants.py
│   └── test_exceptions.py
├── alembic/
├── alembic.ini
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── .env.example
├── .gitignore
└── Dockerfile
```

## Detailed Requirements

### 1. `config.py` — Settings Management
Create a `Settings` class inheriting from `pydantic_settings.BaseSettings`. It must include:
- `DATABASE_URL`: str — PostgreSQL async connection URL (e.g., `postgresql+asyncpg://...`)
- `DATABASE_URL_SYNC`: str — Sync URL for Alembic migrations
- `TELEGRAM_BOT_TOKEN`: str
- `WEBAPP_URL`: str — Telegram Web App URL
- `ADMIN_DASHBOARD_URL`: str
- `ADMIN_API_KEY`: str — Simple API key for admin endpoints (kept as fallback)
- `JWT_SECRET_KEY`: str — Secret key for JWT token signing
- `JWT_ALGORITHM`: str = "HS256"
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`: int = 60
- `LOG_LEVEL`: str = "INFO"
- `ENVIRONMENT`: str = "dev" — (dev / staging / production)
- `CRON_WEEKLY_OPEN_DAY`: str = "sunday"
- `CRON_WEEKLY_OPEN_HOUR`: str = "09:00"

All values must be read from `.env` file — **zero hard coding**. Include a `get_settings()` function with `@lru_cache` for singleton access.

### 2. `database.py` — Async Database Setup
- Create `async_engine` using `create_async_engine(settings.DATABASE_URL)`
- Create `async_session_factory` using `async_sessionmaker`
- Provide `get_db_session()` async generator yielding `AsyncSession`

### 3. `logging_config.py` — Structured Logging
- Function `setup_logging(log_level: str, environment: str)`
- JSON formatter for structured logs
- Log rotation (RotatingFileHandler or TimedRotatingFileHandler)
- Different log levels per environment (dev=DEBUG, production=WARNING)
- Logger name: "ilutzim"

### 4. `messages.py` — Centralized Hebrew Messages
Create a `Messages` class (frozen dataclass or class with class variables) that contains **ALL** Hebrew text used anywhere in the system. Every message must be a class-level constant. No Hebrew text should exist outside this file.

Required message constants:
```
# Bot messages
BOT_WELCOME — Welcome message asking to share contact
BOT_SHARE_CONTACT_BUTTON — Button text for contact sharing
BOT_AUTH_SUCCESS — Successful authentication confirmation
BOT_AUTH_FAIL — Phone number not found in system
BOT_WEEK_OPEN — Weekly notification that submission window is open
BOT_REMINDER — Reminder for guards who haven't submitted
BOT_SUBMISSION_SUMMARY — Template for submission summary (with placeholders)
BOT_DEVIATION_WARNING — Template for deviation warning (with placeholders)
BOT_LOCKOUT — Message when week is locked/published
BOT_SUBMIT_ANYWAY — Message for manual override option
BOT_OPEN_WEBAPP_BUTTON — Button text to open the web app

# Error messages
ERR_WEEK_LOCKED — Week is locked, cannot submit
ERR_USER_NOT_FOUND — User not found
ERR_USER_DEACTIVATED — User account is deactivated
ERR_AUTH_FAILED — Authentication failed
ERR_CONFLICT — Concurrent modification conflict
ERR_VALIDATION — Validation error

# UI Labels
LABEL_AVAILABLE — "זמין"
LABEL_UNAVAILABLE — "לא זמין"
LABEL_BLOCKED — "חסום"
LABEL_MORNING — "בוקר"
LABEL_AFTERNOON — "צהריים"
LABEL_NIGHT — "לילה"

# Excel export labels
EXCEL_HEADER_NAME — "שם"
EXCEL_HEADER_PHONE — "טלפון"
EXCEL_HEADER_NOTES — "הערות"
EXCEL_HEADER_THRESHOLDS — "סף מינימום"
EXCEL_HEADER_DEVIATION — "חריגה"
EXCEL_REPORT_TITLE — Template: "דוח משמרות — {start} עד {end}"

# Event type labels
EVENT_VACATION — "חופשה"
EVENT_MILITARY — "מילואים"
EVENT_FIREARMS — "רענון נשק"

# Submission status labels
STATUS_SUBMITTED — "הוגש"
STATUS_SUBMITTED_VARIANCE — "הוגש עם חריגה"
STATUS_PENDING — "ממתין להגשה"
STATUS_AUTO_ABSENCE — "העדרות אוטומטית"
```

The actual Hebrew text for bot messages should follow the PRD specification closely.

### 5. `constants.py` — Enums & Constants
Create the following Enums (using Python `enum.Enum` with string values):
- `ShiftType`: morning, afternoon, night
- `WeekStatus`: open, locked, published
- `EventType`: vacation, military_reserve, firearms_training
- `SubmissionStatus`: submitted, submitted_with_variance, pending, auto_absence
- `UserRole`: guard, shift_lead, scanner
- `AdminRole`: super_admin, admin, viewer (permissions: super_admin = full access, admin = manage guards/weeks/events, viewer = read-only)

### 6. `exceptions.py` — Custom Exceptions & Global Handlers
Base exception class:
```python
class AppBaseException(Exception):
    status_code: int
    message: str  # Should reference Messages constants
```

Subclasses:
- `WeekLockedException(AppBaseException)` — status 403
- `UserNotAuthorizedException(AppBaseException)` — status 401
- `UserDeactivatedException(AppBaseException)` — status 403
- `UserNotFoundException(AppBaseException)` — status 404
- `ValidationException(AppBaseException)` — status 422
- `ConflictException(AppBaseException)` — status 409
- `AdminNotFoundException(AppBaseException)` — status 404
- `InvalidCredentialsException(AppBaseException)` — status 401
- `TokenExpiredException(AppBaseException)` — status 401
- `InsufficientPermissionsException(AppBaseException)` — status 403

Global FastAPI exception handlers:
- `app_exception_handler` — catches `AppBaseException`, returns JSON `{"success": false, "error": message, "detail": null}`
- `validation_exception_handler` — catches Pydantic `RequestValidationError`
- `generic_exception_handler` — catches `Exception`, logs traceback, returns 500

### 7. `dependencies.py` — Dependency Injection
- `get_db()` — async generator yielding `AsyncSession` from `database.py`
- `get_current_user()` — placeholder (returns None for now, will be implemented in Step 5)

### 8. `main.py` — FastAPI Application Factory
- `create_app()` function returning FastAPI instance
- `lifespan` async context manager for startup/shutdown
- On startup: call `setup_logging()`, log "Application starting"
- CORS middleware with origins from config (WEBAPP_URL, ADMIN_DASHBOARD_URL)
- Register global exception handlers
- Health check endpoint: `GET /health` → `{"status": "ok"}`

### 9. `.env.example`
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ilutzim
DATABASE_URL_SYNC=postgresql://user:password@localhost:5432/ilutzim
TELEGRAM_BOT_TOKEN=your-bot-token-here
WEBAPP_URL=https://your-webapp-url.com
ADMIN_DASHBOARD_URL=https://your-admin-url.com
ADMIN_API_KEY=your-admin-api-key
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
LOG_LEVEL=INFO
ENVIRONMENT=dev
CRON_WEEKLY_OPEN_DAY=sunday
CRON_WEEKLY_OPEN_HOUR=09:00
```

### 10. `requirements.txt`
```
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
sqlalchemy[asyncio]>=2.0.25
asyncpg>=0.29.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
aiogram>=3.3.0
openpyxl>=3.1.2
alembic>=1.13.0
python-dotenv>=1.0.0
apscheduler>=3.10.4
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
```

### 11. `requirements-dev.txt`
```
-r requirements.txt
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
httpx>=0.27.0
aiosqlite>=0.20.0
factory-boy>=3.3.0
freezegun>=1.4.0
```

### 12. `pyproject.toml`
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
filterwarnings = ["ignore::DeprecationWarning"]

[tool.coverage.run]
source = ["app"]
omit = ["tests/*", "alembic/*"]
```

### 13. `.gitignore`
Include standard Python gitignore + `.env`, `__pycache__`, `.pytest_cache`, `*.pyc`, `alembic/versions/*.py` (optional), IDE files.

## Tests Required

### `tests/conftest.py`
- Fixture `test_settings` — creates `Settings` with test values (SQLite async DB URL)
- Fixture `test_engine` — creates async engine for SQLite (`aiosqlite`)
- Fixture `test_session` — yields `AsyncSession` from test engine, rolls back after each test
- Fixture `test_app` — creates FastAPI app with dependency overrides
- Fixture `test_client` — `httpx.AsyncClient` bound to test app

### `tests/test_config.py`
1. `test_settings_loads_from_env` — Settings loads values from environment variables
2. `test_settings_has_all_required_fields` — All required fields are present
3. `test_settings_default_values` — LOG_LEVEL defaults to "INFO", ENVIRONMENT defaults to "dev"
4. `test_get_settings_returns_singleton` — `get_settings()` returns the same instance (lru_cache)

### `tests/test_messages.py`
1. `test_all_message_attributes_are_non_empty` — Every attribute in Messages is a non-empty string
2. `test_all_messages_contain_hebrew` — Every message contains at least one Hebrew character (Unicode range)
3. `test_no_duplicate_messages` — No two attributes have identical values
4. `test_bot_messages_exist` — All BOT_* constants exist
5. `test_error_messages_exist` — All ERR_* constants exist
6. `test_label_messages_exist` — All LABEL_* constants exist

### `tests/test_constants.py`
1. `test_shift_type_values` — ShiftType has morning, afternoon, night
2. `test_week_status_values` — WeekStatus has open, locked, published
3. `test_event_type_values` — EventType has vacation, military_reserve, firearms_training
4. `test_submission_status_values` — All 4 statuses exist
5. `test_user_role_values` — UserRole has guard, shift_lead, scanner

### `tests/test_exceptions.py`
1. `test_week_locked_exception_status_code` — status_code == 403
2. `test_user_not_authorized_status_code` — status_code == 401
3. `test_user_not_found_status_code` — status_code == 404
4. `test_conflict_exception_status_code` — status_code == 409
5. `test_global_handler_returns_json` — Exception handler returns proper JSON structure via test client
6. `test_health_check_endpoint` — `GET /health` returns 200 with `{"status": "ok"}`

## Rules
- Full OOP with separation of concerns (Controllers → Services → Repositories)
- Zero hard coding — every configurable value comes from config or .env
- All Hebrew text centralized in `messages.py` only
- Error handling and logging from day one
- Full type hints everywhere
- Async/await where relevant
- All tests must pass when running `pytest`
- Code comments in English
