# Step 4 — Services (Business Logic Layer) & Tests

## Context
You are continuing development of the Micro-SaaS security guard shift constraint management system. **Steps 0-3 (infrastructure, models, repositories, schemas) are complete. All previous tests pass.**

**Important:** All user-facing text is in Hebrew (centralized in `messages.py`). Code comments in English.

## Objective
Build the business logic layer — service classes that orchestrate repositories, enforce rules, compute deviations, handle smart skip filtering, and generate notification text. Write comprehensive tests covering all business scenarios.

## Files to Create (in `app/services/`)

### 1. `user_service.py` — `UserService`
Constructor receives `UserRepository` via DI.

Methods:
- `create_user(data: UserCreate) -> UserResponse` — create and return
- `update_user(user_id: UUID, data: UserUpdate) -> UserResponse` — update and return
- `deactivate_user(user_id: UUID) -> UserResponse` — set is_active=False
- `get_all_active_users() -> list[UserResponse]` — active users only
- `get_user(user_id: UUID) -> UserResponse` — raises `UserNotFoundException` if not found
- `link_telegram(phone_number: str, telegram_id: str) -> UserResponse` — bot authentication flow: find by phone, link telegram_id; raises `UserNotFoundException` if phone not in DB

### 2. `week_service.py` — `WeekService`
Constructor receives `ScheduleWeekRepository` via DI.

Methods:
- `create_week(data: WeekCreate) -> WeekResponse`
- `get_all_weeks() -> list[WeekResponse]`
- `change_week_status(week_id: UUID, new_status: WeekStatus) -> WeekResponse`
- `get_current_open_week() -> WeekResponse | None`
- `validate_week_is_open(week_id: UUID) -> None` — raises `WeekLockedException` if status is not `open`

### 3. `submission_service.py` — `SubmissionService` (Core Business Logic)
Constructor receives: `SubmissionRepository`, `UserRepository`, `WeekService`, `EventService` via DI.

Methods:
- **`submit_constraints(user_id: UUID, data: SubmissionCreate) -> SubmissionResponse`** — Main flow:
  1. Validate the week is open (via `WeekService.validate_week_is_open`)
  2. Validate the user exists and `is_active=True` (raise `UserDeactivatedException` if not)
  3. Get blocked dates for the user in this week (via `EventService`)
  4. Filter out blocked dates from submitted days — if user submitted a blocked date, silently ignore it with a log warning
  5. Upsert the submission via repository
  6. **Deviation detection:**
     - Count total shifts marked as available across all days
     - Count night shifts (shift_type == night)
     - Count evening/afternoon shifts (shift_type == afternoon)
     - Compare against user's `min_total_shifts`, `min_night_shifts`, `min_evening_shifts`
     - Set `has_deviation=True` if **any** threshold is not met
     - Build `DeviationDetail` list for response
  7. Return full response including deviation details

- `get_submission(user_id: UUID, week_id: UUID) -> SubmissionResponse | None`
- `get_submission_status_grid(week_id: UUID) -> list[SubmissionStatusGrid]` — Build status table: for each active user, determine status (submitted/submitted_with_variance/pending/auto_absence)
- `get_missing_users(week_id: UUID) -> list[UserResponse]` — Users who haven't submitted

### 4. `event_service.py` — `EventService`
Constructor receives `ScheduleEventRepository` via DI.

Methods:
- `create_event(data: ScheduleEventCreate) -> ScheduleEventResponse`
- `delete_event(event_id: UUID) -> bool`
- `get_user_events_for_week(user_id: UUID, week_start: date, week_end: date) -> list[ScheduleEventResponse]`
- `get_blocked_dates_for_user(user_id: UUID, start_date: date, end_date: date) -> list[BlockedDateInfo]` — Expand events into individual blocked dates with labels (from `messages.py`)
- `is_user_fully_absent(user_id: UUID, start_date: date, end_date: date) -> bool` — True if any event covers the entire date range (for smart skip logic)

### 5. `notification_service.py` — `NotificationService`
Constructor receives `EventService`, `SubmissionRepository`, `UserRepository` via DI.

Methods:
- `get_users_to_notify(week_id: UUID) -> tuple[list[User], list[User]]` — Returns (to_notify, skipped_auto_absence). Uses `EventService.is_user_fully_absent()` for smart skip.
- `build_submission_summary(submission: WeeklySubmission, user: User) -> str` — Build Hebrew summary text showing: each day → available/unavailable → shift windows. Uses templates from `messages.py`.
- `build_deviation_warning(user: User, deviation_details: list[DeviationDetail]) -> str | None` — Build Hebrew warning text showing which thresholds were not met. Returns None if no deviation.

### 6. `export_service.py` — `ExportService` (Placeholder)
- `generate_excel(week_id: UUID) -> bytes` — Placeholder returning empty bytes for now. Full implementation in Step 9.

### 7. `auth_service.py` — `AuthService` (Admin Authentication)
Constructor receives `AdminRepository` via DI. Uses `passlib[bcrypt]` for hashing and `python-jose` for JWT.

Methods:
- `register_admin(email: str, password: str, full_name: str, role: AdminRole = AdminRole.admin, inviting_admin_role: AdminRole) -> dict`:
  - Only `super_admin` can create new admins
  - Validate email format
  - Check email uniqueness → `ConflictException` if exists
  - Hash password with bcrypt
  - Create admin via repository
  - Return admin response dict (never include password_hash)
  
- `login(email: str, password: str) -> dict`:
  - Find admin by email → `InvalidCredentialsException` if not found
  - Verify password with bcrypt → `InvalidCredentialsException` if wrong
  - Verify `is_active=True` → `UserDeactivatedException` if not
  - Generate JWT token with payload: `{sub: admin_id, email, role, exp}`
  - Return `{"access_token": token, "token_type": "bearer", "admin": {...}}`

- `verify_token(token: str) -> dict`:
  - Decode JWT with secret key and algorithm from config
  - Handle ExpiredSignatureError → `TokenExpiredException`
  - Handle JWTError → `UserNotAuthorizedException`
  - Verify admin still exists and is active
  - Return decoded payload

- `get_current_admin(token: str) -> Admin`:
  - Call `verify_token(token)`
  - Get admin from DB by ID from payload
  - Return Admin object

- `change_password(admin_id: int, current_password: str, new_password: str) -> bool`:
  - Verify current password
  - Hash new password
  - Update via repository

- `get_all_admins() -> list[dict]` — Return list of admin info (no passwords)

- `require_permission(admin: Admin, minimum_role: AdminRole) -> None`:
  - Role hierarchy: super_admin > admin > viewer
  - Raise `InsufficientPermissionsException` if admin role is below minimum

### 8. `settings_service.py` — `SettingsService`
Constructor receives `SystemSettingsRepository` via DI.

Methods:
- `get_default_shift_times() -> DefaultShiftTimesResponse`
- `update_setting(data: SystemSettingUpdate) -> SystemSettingResponse`
- `get_all_settings() -> list[SystemSettingResponse]`

### 9. `__init__.py`
Import all service classes.

## Tests Required (`tests/test_services.py`)

All tests use real test DB (not mocks) with fixtures from `conftest.py`.

### UserService (5 tests)
1. `test_create_user_success` — Create user → verify returned response
2. `test_create_user_duplicate_phone` — Duplicate phone → ConflictException or IntegrityError
3. `test_deactivate_user` — Deactivate → verify is_active=False
4. `test_link_telegram_success` — Link telegram_id → verify stored
5. `test_link_telegram_phone_not_found` — Non-existent phone → UserNotFoundException

### WeekService (5 tests)
6. `test_create_week` — Create week → verify response
7. `test_change_status_open_to_locked` — Change status → verify
8. `test_validate_week_is_open_success` — Open week → no exception
9. `test_validate_week_is_open_locked` — Locked week → WeekLockedException
10. `test_validate_week_is_open_published` — Published week → WeekLockedException

### SubmissionService (10 tests — most critical)
11. `test_submit_constraints_success` — Valid submission, no deviations → has_deviation=False
12. `test_submit_constraints_with_deviation` — User with min_total_shifts=5 submits 3 shifts → has_deviation=True, deviation_details populated
13. `test_submit_constraints_night_deviation` — User with min_night_shifts=2 submits 1 night shift → deviation
14. `test_submit_constraints_no_deviation` — Submission meets all thresholds → has_deviation=False
15. `test_submit_to_locked_week` — Submit to locked week → WeekLockedException
16. `test_submit_deactivated_user` — Deactivated user submits → UserDeactivatedException
17. `test_submit_filters_blocked_dates` — Submit includes a blocked date → that date is silently filtered, remaining days saved
18. `test_upsert_overwrites_previous` — Submit twice for same user+week → only latest data exists
19. `test_submission_status_grid` — Create mixed data → verify grid shows correct statuses per user
20. `test_get_missing_users` — Some submitted, some not → correct missing list

### EventService (4 tests)
21. `test_create_event` — Create blockout event → verify
22. `test_get_blocked_dates` — Get blocked dates → correct list with labels
23. `test_is_user_fully_absent_true` — Event covers entire week → True
24. `test_is_user_fully_absent_false` — Partial event → False

### NotificationService (4 tests)
25. `test_get_users_to_notify_filters_absent` — Fully absent users filtered to skipped list
26. `test_build_submission_summary` — Summary text contains Hebrew, has day names and shift details
27. `test_build_deviation_warning` — Warning text contains threshold details
28. `test_build_deviation_warning_none` — No deviation → returns None

### AuthService (8 tests)
29. `test_login_success` — Login with correct email+password → returns JWT token + admin info (never includes password_hash)
30. `test_login_wrong_password` — Correct email, wrong password → InvalidCredentialsException
31. `test_login_nonexistent_email` — Email not in DB → InvalidCredentialsException
32. `test_login_deactivated_admin` — Deactivated admin tries to login → UserDeactivatedException
33. `test_verify_token_valid` — Verify a freshly generated JWT → returns decoded payload with sub, email, role
34. `test_verify_token_expired` — Verify an expired JWT → TokenExpiredException
35. `test_verify_token_invalid` — Verify a tampered/garbage token → UserNotAuthorizedException
36. `test_register_admin_by_super_admin` — super_admin registers new admin → success, admin created with correct role
37. `test_register_admin_by_regular_admin` — regular admin tries to register → InsufficientPermissionsException
38. `test_register_admin_duplicate_email` — Register with existing email → ConflictException
39. `test_change_password_success` — Change password with correct current password → success, new password works
40. `test_change_password_wrong_current` — Change password with wrong current password → InvalidCredentialsException
41. `test_require_permission_hierarchy` — super_admin passes all checks; admin passes admin/viewer checks but fails super_admin; viewer passes only viewer check

## Rules
- Every service receives its repositories via constructor (DI pattern)
- Business logic ONLY — no direct DB access (all through repositories)
- Comprehensive error handling with custom exceptions
- Logging at every significant operation (info for success, warning for edge cases, error for failures)
- All Hebrew text from `messages.py` only
- Full type hints
- Async/await everywhere
- All tests must pass with `pytest`
- Code comments in English
