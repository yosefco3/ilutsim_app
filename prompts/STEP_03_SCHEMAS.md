# Step 3 — Pydantic Schemas (Validation Layer) & Tests

## Context
You are continuing development of the Micro-SaaS security guard shift constraint management system. **Steps 0-2 (infrastructure, models, repositories) are complete. All previous tests pass.**

**Important:** All user-facing text is in Hebrew (centralized in `messages.py`). Code comments in English.

## Objective
Create Pydantic v2 schemas for all API input validation and output serialization, including custom validators for Israeli phone numbers, date logic, and shift constraints. Write comprehensive validation tests.

## Files to Create (in `app/schemas/`)

### 1. `user_schemas.py`
- `UserCreate`: phone_number (str, validated), full_name (str), role (UserRole), exemptions_notes (str | None), min_total_shifts (int = 0), min_night_shifts (int = 0), min_evening_shifts (int = 0)
- `UserUpdate`: All fields optional
- `UserResponse`: All fields + id (UUID), is_active (bool), telegram_id (str | None), created_at (datetime) — `model_config = ConfigDict(from_attributes=True)`
- `UserListResponse`: users (list[UserResponse]), count (int)

### 2. `week_schemas.py`
- `WeekCreate`: start_date (date), end_date (date) — validator: start_date < end_date
- `WeekStatusUpdate`: status (WeekStatus)
- `WeekResponse`: All fields + id (UUID), status (WeekStatus) — `from_attributes=True`

### 3. `event_schemas.py`
- `ScheduleEventCreate`: user_id (UUID), event_type (EventType), start_date (date), end_date (date) — validator: start_date <= end_date
- `ScheduleEventResponse`: All fields + id (UUID) — `from_attributes=True`
- `BlockedDateInfo`: date (date), event_type (EventType), label (str)

### 4. `submission_schemas.py` — Core Schemas
- `ShiftWindowInput`: shift_type (ShiftType), start_time (time), end_time (time) — validator: start_time != end_time
- `ShiftWindowResponse`: Same + id (UUID) — `from_attributes=True`
- `DayStatusInput`: date (date), is_available (bool), shifts (list[ShiftWindowInput])
  - Validator: if is_available=False → shifts must be empty
  - Validator: if is_available=True → shifts must have at least one entry
- `DayStatusResponse`: Same + id (UUID), shift_windows (list[ShiftWindowResponse]) — `from_attributes=True`
- `SubmissionCreate`: week_id (UUID), general_notes (str | None), days (list[DayStatusInput])
  - Validator: days must contain at least one entry
- `SubmissionResponse`: All data including nested days and shifts + has_deviation (bool), submitted_at (datetime) — `from_attributes=True`
- `SubmissionStatusGrid`: user_id (UUID), full_name (str), phone_number (str), status (SubmissionStatus), submitted_at (datetime | None), has_deviation (bool)
- `DeviationDetail`: rule_name (str), required (int), actual (int)

### 5. `settings_schemas.py`
- `SystemSettingUpdate`: setting_key (str), setting_value (str), description (str | None)
- `SystemSettingResponse`: setting_key (str), setting_value (str), description (str | None)
- `DefaultShiftTimesResponse`: morning_start (time), morning_end (time), afternoon_start (time), afternoon_end (time), night_start (time), night_end (time)

### 6. `common_schemas.py`
- `ApiResponse`: success (bool), message (str), data (Any | None)
- `ErrorResponse`: success (bool = False), error (str), detail (str | None)

### Custom Validators

**Phone number validation:**
- Israeli format: starts with "05" and has 10 digits, OR starts with "+972" followed by 9 digits
- Strip spaces, dashes before validation
- Validation error message from `messages.py`

**Night shift crossing midnight:**
- For ShiftType.night: `start_time > end_time` is valid (e.g., 23:00 → 07:00)
- For other shifts: `start_time < end_time` is required

## Tests Required (`tests/test_schemas.py`)

### UserSchemas
1. `test_user_create_valid` — Valid data → no error
2. `test_user_create_invalid_phone` — Invalid phone (e.g., "1234") → ValidationError
3. `test_user_create_valid_phone_formats` — "0501234567", "+972501234567", "050-123-4567" → all valid after normalization
4. `test_user_update_partial` — Only name provided → valid (all fields optional)
5. `test_user_response_from_orm` — Convert ORM model to response schema → works correctly

### WeekSchemas
6. `test_week_create_valid` — Valid date range → no error
7. `test_week_create_end_before_start` — end_date before start_date → ValidationError
8. `test_week_status_update_valid_enum` — Valid status → no error
9. `test_week_status_update_invalid_enum` — Invalid status string → ValidationError

### SubmissionSchemas
10. `test_submission_create_valid_full` — Full submission with days and shifts → valid
11. `test_submission_create_unavailable_no_shifts` — Unavailable day with no shifts → valid
12. `test_submission_create_unavailable_with_shifts` — Unavailable day WITH shifts → ValidationError
13. `test_submission_create_available_no_shifts` — Available day with no shifts → ValidationError
14. `test_shift_window_night_crosses_midnight` — Night shift 23:00-07:00 → valid
15. `test_shift_window_same_start_end` — start_time == end_time → ValidationError
16. `test_submission_create_empty_days` — Empty days list → ValidationError

### EventSchemas
17. `test_event_create_valid` — Valid event → no error
18. `test_event_create_end_before_start` — end_date < start_date → ValidationError

## Rules
- Pydantic v2 style: `model_config = ConfigDict(...)`, `field_validator`, `model_validator`
- Full type hints
- All validation error messages reference `messages.py` Hebrew strings
- `from_attributes=True` for ORM model conversion
- All tests must pass with `pytest`
- Code comments in English
