# Step 5 — Controllers (API Routes), Telegram initData Auth & Tests

## Context
You are continuing development of the Micro-SaaS security guard shift constraint management system. **Steps 0-4 (infrastructure, models, repositories, schemas, services) are complete. All previous tests pass.**

**Important:** All user-facing text is in Hebrew (centralized in `messages.py`). Code comments in English.

## Objective
Build the API layer — thin controller classes that delegate to services, implement Telegram initData HMAC-SHA256 authentication, simple admin API key auth, and write integration tests for all endpoints.

## Telegram initData Authentication

### `app/utils/telegram_auth.py`
Implement Telegram Web App initData validation per the official specification:

```python
def validate_telegram_init_data(init_data: str, bot_token: str) -> dict:
    """
    Validate Telegram Web App initData using HMAC-SHA256.
    
    1. Parse init_data as URL query string (urllib.parse.parse_qs)
    2. Extract 'hash' value, remove it from params
    3. Build data_check_string: sorted key=value pairs joined with \n
    4. Compute secret_key = HMAC-SHA256(key=b"WebAppData", msg=bot_token.encode())
    5. Compute hash = HMAC-SHA256(key=secret_key, msg=data_check_string.encode()).hexdigest()
    6. Compare computed hash with provided hash (constant-time comparison)
    7. Extract and parse 'user' JSON object → get telegram_id
    8. Validate auth_date is not older than 24 hours
    9. Raise UserNotAuthorizedException on any failure
    10. Return parsed user dict on success
    """
```

### Update `app/dependencies.py`
Implement the real `get_current_user()`:
```python
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    1. Extract 'Authorization: Bearer <initData>' from request header
    2. Call validate_telegram_init_data(init_data, settings.TELEGRAM_BOT_TOKEN)
    3. Extract telegram_id from result
    4. Look up User by telegram_id via UserRepository
    5. Verify is_active=True
    6. Raise UserNotAuthorizedException if not found
    7. Raise UserDeactivatedException if not active
    8. Return User object
    """
```

### Admin JWT Authentication
```python
async def get_current_admin(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Admin:
    """
    1. Extract 'Authorization: Bearer <jwt_token>' from request header
    2. Call auth_service.verify_token(token)
    3. Get admin from DB via AuthService.get_current_admin()
    4. Raise UserNotAuthorizedException if invalid/expired
    5. Return Admin object (with role for permission checks)
    """

async def require_super_admin(admin: Admin = Depends(get_current_admin)) -> Admin:
    """Shortcut: requires AdminRole.super_admin. Used for creating new admins."""

async def require_admin(admin: Admin = Depends(get_current_admin)) -> Admin:
    """Shortcut: requires AdminRole.admin or above. Used for CUD operations."""

async def require_viewer(admin: Admin = Depends(get_current_admin)) -> Admin:
    """Shortcut: requires AdminRole.viewer or above. Used for read operations."""
```

## Controllers (in `app/controllers/`)

### 0. `auth_controller.py` — Prefix: `/api/auth`
Public endpoints (no auth required for login/register):

| Method | Path | Description | Auth | Response |
|--------|------|-------------|------|----------|
| POST | `/login` | Admin login (email + password) | None | `{"access_token", "token_type", "admin"}` |
| POST | `/register` | Register new admin | super_admin JWT | Admin response (201) |
| GET | `/me` | Get current admin profile | Any admin JWT | Admin response |
| POST | `/change-password` | Change own password | Any admin JWT | Success message |

Note: The first super_admin is created via the Alembic seed migration. They can then create additional admins via the `/register` endpoint.

### 1. `submission_controller.py` — Prefix: `/api/submissions`
All endpoints require `Depends(get_current_user)`.

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/{week_id}` | Get existing submission for current user | SubmissionResponse or null |
| POST | `/` | Submit/update constraints | SubmissionResponse (201) |
| GET | `/{week_id}/blocked-dates` | Get blocked dates for current user | list[BlockedDateInfo] |
| GET | `/{week_id}/defaults` | Get default shift times + week status | DefaultShiftTimesResponse + WeekStatus |

### 2. `admin_users_controller.py` — Prefix: `/api/admin/users`
All endpoints require `Depends(require_admin)` (admin role or above).

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/` | List all guards | UserListResponse |
| POST | `/` | Create new guard | UserResponse (201) |
| PUT | `/{user_id}` | Update guard | UserResponse |
| PATCH | `/{user_id}/deactivate` | Deactivate guard | UserResponse |

### 3. `admin_weeks_controller.py` — Prefix: `/api/admin/weeks`
All endpoints require `Depends(require_admin)` (admin role or above).

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/` | List all weeks | list[WeekResponse] |
| POST | `/` | Create new week | WeekResponse (201) |
| PATCH | `/{week_id}/status` | Change week status | WeekResponse |
| GET | `/{week_id}/status-grid` | Get submission status grid | list[SubmissionStatusGrid] |

### 4. `admin_events_controller.py` — Prefix: `/api/admin/events`
All endpoints require `Depends(require_admin)` (admin role or above).

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/` | List events (optional user_id filter) | list[ScheduleEventResponse] |
| POST | `/` | Create blockout event | ScheduleEventResponse (201) |
| DELETE | `/{event_id}` | Delete event | ApiResponse |

### 5. `admin_notifications_controller.py` — Prefix: `/api/admin/notifications`
Requires `Depends(require_admin)`.

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| POST | `/{week_id}/send-reminder` | Send reminders to non-submitters | ApiResponse with count |

Note: This endpoint is a placeholder in this step — returns the list of users who would be notified. Full Telegram integration happens in Step 6.

### 6. `admin_export_controller.py` — Prefix: `/api/admin/export`
Requires `Depends(require_viewer)` (viewer or above — read-only access sufficient).

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/{week_id}/excel` | Export week data as Excel | StreamingResponse (xlsx) |

### 7. `admin_settings_controller.py` — Prefix: `/api/admin/settings`
Requires `Depends(require_admin)`.

### 8. `admin_admins_controller.py` — Prefix: `/api/admin/admins`
Endpoints for managing admin users themselves.

| Method | Path | Description | Auth | Response |
|--------|------|-------------|------|----------|
| GET | `/` | List all admins | super_admin | list[AdminResponse] |
| PATCH | `/{admin_id}/role` | Change admin role | super_admin | AdminResponse |
| PATCH | `/{admin_id}/deactivate` | Deactivate admin | super_admin | AdminResponse |

Note: Only super_admin can manage other admins.

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/` | Get all system settings | list[SystemSettingResponse] |
| PUT | `/` | Update a system setting | SystemSettingResponse |

### Update `main.py`
- Register all routers with correct prefixes and tags
- CORS middleware with allowed origins from config
- Global exception handlers registered

## Tests Required

### `tests/test_telegram_auth.py` (6 tests)
1. `test_validate_valid_init_data` — Construct valid initData with correct HMAC → returns user dict
2. `test_validate_invalid_hash` — Tampered hash → UserNotAuthorizedException
3. `test_validate_missing_hash` — initData without hash field → exception
4. `test_validate_expired_auth_date` — auth_date older than 24 hours → exception
5. `test_validate_extracts_telegram_id` — Correct telegram_id extracted from user JSON
6. `test_validate_with_wrong_bot_token` — Different bot token → hash mismatch → exception

Helper: Create a `generate_test_init_data(bot_token, user_data, auth_date)` helper function that constructs valid initData strings for testing.

### `tests/test_api_submissions.py` (8 tests)
All tests use `httpx.AsyncClient` with test app. Override `get_current_user` dependency to inject a test user.

7. `test_get_submission_success` — GET existing submission → 200 + data
8. `test_get_submission_not_found` — GET non-existent → 200 + null data
9. `test_post_submission_success` — POST valid submission → 201 + response
10. `test_post_submission_locked_week` — POST to locked week → 403
11. `test_post_submission_unauthorized` — No auth header → 401
12. `test_post_submission_deactivated_user` — Deactivated user → 403
13. `test_get_blocked_dates` — GET blocked dates → 200 + list
14. `test_get_defaults` — GET defaults → 200 + shift times

### `tests/test_api_auth.py` (8 tests)
1. `test_admin_login_success` — POST /api/auth/login with correct credentials → 200 + JWT token
2. `test_admin_login_wrong_password` — Wrong password → 401
3. `test_admin_login_nonexistent_email` — Unknown email → 401
4. `test_admin_login_deactivated` — Deactivated admin → 403
5. `test_admin_register_by_super_admin` — Super admin creates new admin → 201
6. `test_admin_register_by_regular_admin` — Regular admin tries → 403
7. `test_admin_get_me` — GET /api/auth/me with valid JWT → 200 + admin profile
8. `test_admin_expired_token` — Expired JWT → 401

Helper: Create a `get_admin_token(client, email, password)` helper that logs in and returns the JWT token for use in other tests.

### `tests/test_api_admin.py` (12 tests)
All tests include `Authorization: Bearer <jwt_token>` header.

9. `test_admin_list_users` — GET /api/admin/users → 200 + list
10. `test_admin_create_user` — POST → 201 + user
11. `test_admin_update_user` — PUT → 200 + updated user
12. `test_admin_deactivate_user` — PATCH → 200 + deactivated
13. `test_admin_create_week` — POST → 201 + week
14. `test_admin_change_week_status` — PATCH → 200 + updated
15. `test_admin_status_grid` — GET → 200 + grid data
16. `test_admin_create_event` — POST → 201
17. `test_admin_delete_event` — DELETE → 200
18. `test_admin_get_settings` — GET → 200
19. `test_admin_update_setting` — PUT → 200
20. `test_admin_no_token` — Any admin endpoint without JWT → 401

## Rules
- Controllers are thin — delegate all logic to services
- Dependency injection via FastAPI `Depends()` for services, repositories, and session
- Proper HTTP status codes (200, 201, 401, 403, 404, 409, 422)
- Logging at each endpoint (request received, response status)
- Full type hints
- Response models defined in schemas
- Tests use `httpx.AsyncClient` with dependency overrides
- All tests must pass with `pytest`
- Code comments in English
