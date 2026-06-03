# Step 2 — Repositories (Data Access Layer) & Tests

## Context
You are continuing development of the Micro-SaaS security guard shift constraint management system. **Steps 0-1 (infrastructure + database models) are complete. All previous tests pass.**

**Important:** All user-facing text is in Hebrew (centralized in `messages.py`). Code comments in English.

## Objective
Build the Data Access Layer — a generic base repository and specialized repository classes for each entity, with full async CRUD operations and comprehensive tests.

## Files to Create (in `app/repositories/`)

### 1. `base_repository.py` — Generic Base Repository
```python
class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model_class: Type[T]):
        ...

    async def get_by_id(self, id: UUID) -> T | None
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[T]
    async def create(self, **kwargs) -> T
    async def update(self, id: UUID, **kwargs) -> T
    async def delete(self, id: UUID) -> bool
    async def save(self, instance: T) -> T  # add + commit + refresh
```
- Accepts `AsyncSession` via constructor (Dependency Injection)
- All methods are async
- Full type hints with Generics
- Uses SQLAlchemy 2.0 `select()`, `update()`, `delete()` statements

### 2. `user_repository.py` — `UserRepository(BaseRepository[User])`
- `get_by_phone(phone_number: str) -> User | None`
- `get_by_telegram_id(telegram_id: str) -> User | None`
- `get_active_users() -> list[User]` — returns only `is_active=True`
- `link_telegram_id(phone_number: str, telegram_id: str) -> User` — find by phone, set telegram_id
- `deactivate_user(user_id: UUID) -> User` — set `is_active=False`

### 3. `schedule_week_repository.py` — `ScheduleWeekRepository`
- `get_current_open_week() -> ScheduleWeek | None` — returns the week with `status=open`
- `get_by_date_range(start: date, end: date) -> ScheduleWeek | None`
- `update_status(week_id: UUID, new_status: WeekStatus) -> ScheduleWeek`

### 4. `schedule_event_repository.py` — `ScheduleEventRepository`
- `get_events_for_user(user_id: UUID, start_date: date, end_date: date) -> list[ScheduleEvent]` — events overlapping the given date range
- `get_full_week_absences(week_start: date, week_end: date) -> list[ScheduleEvent]` — events where start_date <= week_start AND end_date >= week_end (covers entire week)
- `create_event(user_id: UUID, event_type: EventType, start: date, end: date) -> ScheduleEvent`
- `delete_event(event_id: UUID) -> bool`

### 5. `submission_repository.py` — `SubmissionRepository`
- `get_submission(user_id: UUID, week_id: UUID) -> WeeklySubmission | None` — eager load: `daily_statuses` → `shift_windows` using `selectinload`
- `upsert_submission(user_id: UUID, week_id: UUID, data: dict) -> WeeklySubmission`:
  - Check if existing submission exists for user+week
  - If yes: delete old daily_statuses (cascade deletes shift_windows), update submission fields
  - If no: create new submission
  - Create new daily_statuses and shift_windows from data
  - Return the full submission with relationships loaded
- `get_submissions_for_week(week_id: UUID) -> list[WeeklySubmission]` — all submissions for a week, eager loaded
- `get_missing_submissions(week_id: UUID, active_user_ids: list[UUID]) -> list[UUID]` — user IDs from active_user_ids that have no submission for this week
- `get_submission_stats(week_id: UUID) -> dict` — counts: submitted, pending, variance, auto_absence

### 6. `admin_repository.py` — `AdminRepository`
- `get_by_email(email: str) -> Admin | None`
- `get_by_id(admin_id: int) -> Admin | None`
- `create_admin(email: str, password_hash: str, full_name: str, role: AdminRole = AdminRole.admin) -> Admin`
- `get_all_admins() -> list[Admin]`
- `update_admin(admin_id: int, **kwargs) -> Admin` — update name, role, is_active
- `deactivate_admin(admin_id: int) -> Admin`

### 7. `system_settings_repository.py` — `SystemSettingsRepository`
- `get_setting(key: str) -> str | None`
- `set_setting(key: str, value: str, description: str | None = None)` — upsert
- `get_all_settings() -> dict[str, str]` — returns {key: value} dict
- `get_default_shift_times() -> dict` — returns structured dict:
  ```python
  {
      "morning": {"start": "07:00", "end": "15:00"},
      "afternoon": {"start": "15:00", "end": "23:00"},
      "night": {"start": "23:00", "end": "07:00"}
  }
  ```

### 8. `__init__.py`
Import all repository classes for convenient access.

## Tests Required (`tests/test_repositories.py`)

### UserRepository Tests
1. `test_create_and_get_user` — Create a user, get by ID, verify fields
2. `test_get_by_phone_found` — Get by phone number that exists → returns User
3. `test_get_by_phone_not_found` — Get by phone number that doesn't exist → returns None
4. `test_get_by_telegram_id` — Get by telegram_id → returns correct User
5. `test_get_active_users` — Create active + inactive users → only active returned
6. `test_link_telegram_id` — Link telegram_id to existing phone → verify stored
7. `test_link_telegram_id_not_found` — Link to non-existent phone → raises exception or returns None
8. `test_deactivate_user` — Deactivate → verify `is_active=False`

### ScheduleWeekRepository Tests
9. `test_create_and_get_week` — Create week, retrieve, verify fields
10. `test_get_current_open_week` — Create open week → returns it
11. `test_get_current_open_week_none` — No open weeks → returns None
12. `test_update_status` — Change from open to locked → verify

### ScheduleEventRepository Tests
13. `test_create_event` — Create blockout event, verify fields
14. `test_get_events_for_user_in_range` — Events overlapping date range returned
15. `test_get_full_week_absences` — Only events covering the full week returned
16. `test_delete_event` — Delete event → verify gone

### SubmissionRepository Tests
17. `test_upsert_submission_create` — First submission (insert path) → verify created with daily_statuses and shift_windows
18. `test_upsert_submission_update` — Second submission for same user+week (update path) → old data replaced
19. `test_get_submission_with_relations` — Get submission → verify daily_statuses and shift_windows are eagerly loaded
20. `test_get_submissions_for_week` — Multiple submissions → all returned
21. `test_get_missing_submissions` — Some users submitted, some not → correct missing list

### SystemSettingsRepository Tests
22. `test_get_set_setting` — Set a value, get it back → matches
23. `test_get_all_settings` — Multiple settings → all returned as dict
24. `test_get_default_shift_times` — Verify structured output with correct default times

### AdminRepository Tests
25. `test_create_admin` — Create an admin with email, password_hash, full_name, role → verify all fields stored correctly
26. `test_get_admin_by_email_found` — Get admin by email that exists → returns Admin
27. `test_get_admin_by_email_not_found` — Get admin by email that doesn't exist → returns None
28. `test_get_admin_by_id` — Get admin by integer ID → returns correct Admin
29. `test_get_all_admins` — Create multiple admins → all returned
30. `test_update_admin_role` — Update admin role from `admin` to `viewer` → verify changed
31. `test_deactivate_admin` — Deactivate admin → verify `is_active=False`
32. `test_admin_unique_email` — Create two admins with the same email → `IntegrityError`

## Rules
- Each repository receives `AsyncSession` via constructor (DI pattern)
- Async/await everywhere
- Error handling with appropriate logging
- **No business logic** — only data access operations
- Full type hints
- Use SQLAlchemy 2.0 `select()`, `insert()`, `update()` style
- All tests use fixtures from `conftest.py` (test DB with aiosqlite)
- All tests must pass with `pytest`
- Code comments in English
