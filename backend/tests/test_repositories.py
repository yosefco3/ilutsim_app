"""
Tests for the repository layer.
"""

import os
import uuid
from datetime import date, time

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Set test env before importing app
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///test.db")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-token")
os.environ.setdefault("WEBAPP_URL", "http://localhost:3000")
os.environ.setdefault("ADMIN_DASHBOARD_URL", "http://localhost:3001")
os.environ.setdefault("ADMIN_API_KEY", "test-admin-key")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret")
os.environ.setdefault("ENVIRONMENT", "dev")

from app.models.base import Base
from app.models.user import User
from app.models.schedule_week import ScheduleWeek
from app.models.weekly_submission import WeeklySubmission
from app.models.daily_status import DailyStatus
from app.models.shift_window import ShiftWindow
from app.models.schedule_event import ScheduleEvent
from app.models.admin import Admin
from app.models.system_setting import SystemSetting
from app.constants import WeekStatus, ShiftType, EventType, AdminRole, UserRole

from app.repositories.user_repository import UserRepository
from app.repositories.schedule_week_repository import ScheduleWeekRepository
from app.repositories.schedule_event_repository import ScheduleEventRepository
from app.repositories.submission_repository import SubmissionRepository
from app.repositories.admin_repository import AdminRepository
from app.repositories.system_settings_repository import SystemSettingsRepository

# In-memory SQLite
TEST_DB_URL = "sqlite+aiosqlite://"
test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session():
    """Yield a clean in-memory DB session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestSessionLocal() as session:
        yield session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ──────────────── UserRepository ────────────────


class TestUserRepository:
    @pytest.mark.asyncio
    async def test_create_and_get_by_id(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        user = await repo.create(
            phone_number="0501234567",
            first_name="John",
            last_name="Doe",
            is_active=True,
            role=UserRole.BASIC_GUARD,
        )
        await db_session.commit()

        fetched = await repo.get_by_id(user.id)
        assert fetched is not None
        assert fetched.phone_number == "0501234567"
        assert fetched.first_name == "John"
        assert fetched.last_name == "Doe"

    @pytest.mark.asyncio
    async def test_get_by_phone(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        await repo.create(phone_number="0509876543", first_name="Jane", last_name="", is_active=True, role=UserRole.BASIC_GUARD)
        await db_session.commit()

        found = await repo.get_by_phone("0509876543")
        assert found is not None
        assert found.first_name == "Jane"

        not_found = await repo.get_by_phone("0000000000")
        assert not_found is None

    @pytest.mark.asyncio
    async def test_get_by_telegram_id(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        user = await repo.create(phone_number="0501111111", first_name="TG", last_name="User", is_active=True, role=UserRole.BASIC_GUARD)
        user.telegram_id = "123456789"
        await db_session.commit()

        found = await repo.get_by_telegram_id("123456789")
        assert found is not None
        assert found.phone_number == "0501111111"

    @pytest.mark.asyncio
    async def test_get_active_users(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        await repo.create(phone_number="0500000001", first_name="Active", last_name="", is_active=True, role=UserRole.BASIC_GUARD)
        await repo.create(phone_number="0500000002", first_name="Inactive", last_name="", is_active=False, role=UserRole.BASIC_GUARD)
        await db_session.commit()

        active = await repo.get_active_users()
        assert len(active) == 1
        assert active[0].first_name == "Active"

    @pytest.mark.asyncio
    async def test_link_telegram_id(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        await repo.create(phone_number="0502222222", first_name="Link", last_name="Me", is_active=True, role=UserRole.BASIC_GUARD)
        await db_session.commit()

        user = await repo.link_telegram_id_by_phone("0502222222", "999888777")
        assert user.telegram_id == "999888777"

    @pytest.mark.asyncio
    async def test_link_telegram_id_not_found(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        with pytest.raises(ValueError, match="No user found"):
            await repo.link_telegram_id_by_phone("0000000000", "123")

    @pytest.mark.asyncio
    async def test_deactivate_user(self, db_session: AsyncSession):
        repo = UserRepository(db_session)
        user = await repo.create(phone_number="0503333333", first_name="Deac", last_name="", is_active=True, role=UserRole.BASIC_GUARD)
        await db_session.commit()

        deactivated = await repo.deactivate_user(user.id)
        assert deactivated.is_active is False


# ──────────────── ScheduleWeekRepository ────────────────


class TestScheduleWeekRepository:
    @pytest.mark.asyncio
    async def test_create_and_get(self, db_session: AsyncSession):
        repo = ScheduleWeekRepository(db_session)
        week = await repo.create(
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 7),
            status=WeekStatus.OPEN,
        )
        await db_session.commit()

        fetched = await repo.get_by_id(week.id)
        assert fetched is not None
        assert fetched.status == WeekStatus.OPEN

    @pytest.mark.asyncio
    async def test_get_current_open_week(self, db_session: AsyncSession):
        repo = ScheduleWeekRepository(db_session)
        await repo.create(
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 7),
            status=WeekStatus.LOCKED,
        )
        await repo.create(
            start_date=date(2026, 6, 8),
            end_date=date(2026, 6, 14),
            status=WeekStatus.OPEN,
        )
        await db_session.commit()

        open_week = await repo.get_current_open_week()
        assert open_week is not None
        assert open_week.start_date == date(2026, 6, 8)

    @pytest.mark.asyncio
    async def test_get_by_date_range(self, db_session: AsyncSession):
        repo = ScheduleWeekRepository(db_session)
        await repo.create(
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 7),
            status=WeekStatus.OPEN,
        )
        await db_session.commit()

        found = await repo.get_by_date_range(date(2026, 6, 1), date(2026, 6, 7))
        assert found is not None

        not_found = await repo.get_by_date_range(date(2026, 1, 1), date(2026, 1, 7))
        assert not_found is None

    @pytest.mark.asyncio
    async def test_update_status(self, db_session: AsyncSession):
        repo = ScheduleWeekRepository(db_session)
        week = await repo.create(
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 7),
            status=WeekStatus.OPEN,
        )
        await db_session.commit()

        updated = await repo.update_status(week.id, WeekStatus.LOCKED)
        assert updated.status == WeekStatus.LOCKED


# ──────────────── ScheduleEventRepository ────────────────


class TestScheduleEventRepository:
    @pytest.mark.asyncio
    async def test_create_event(self, db_session: AsyncSession):
        # Need a user first
        user_repo = UserRepository(db_session)
        user = await user_repo.create(phone_number="0504444444", first_name="Ev", last_name="User", is_active=True, role=UserRole.BASIC_GUARD)
        await db_session.commit()

        repo = ScheduleEventRepository(db_session)
        event = await repo.create_event(
            user_id=user.id,
            event_type=EventType.VACATION,
            start=date(2026, 6, 5),
            end=date(2026, 6, 10),
        )
        await db_session.commit()

        assert event.id is not None
        assert event.event_type == EventType.VACATION

    @pytest.mark.asyncio
    async def test_get_events_for_user(self, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        user = await user_repo.create(phone_number="0505555555", first_name="Ev2", last_name="", is_active=True, role=UserRole.BASIC_GUARD)
        await db_session.commit()

        repo = ScheduleEventRepository(db_session)
        await repo.create_event(user.id, EventType.VACATION, date(2026, 6, 1), date(2026, 6, 5))
        await repo.create_event(user.id, EventType.MILITARY_RESERVE, date(2026, 6, 20), date(2026, 6, 25))
        await db_session.commit()

        # Query overlapping June 3–June 10
        events = await repo.get_events_for_user(user.id, date(2026, 6, 3), date(2026, 6, 10))
        assert len(events) == 1
        assert events[0].event_type == EventType.VACATION

    @pytest.mark.asyncio
    async def test_get_full_week_absences(self, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        user = await user_repo.create(phone_number="0506666666", first_name="Abs", last_name="", is_active=True, role=UserRole.BASIC_GUARD)
        await db_session.commit()

        repo = ScheduleEventRepository(db_session)
        await repo.create_event(user.id, EventType.VACATION, date(2026, 6, 1), date(2026, 6, 7))
        await repo.create_event(user.id, EventType.MILITARY_RESERVE, date(2026, 6, 3), date(2026, 6, 5))
        await db_session.commit()

        absences = await repo.get_full_week_absences(date(2026, 6, 1), date(2026, 6, 7))
        assert len(absences) == 1
        assert absences[0].event_type == EventType.VACATION


# ──────────────── SubmissionRepository ────────────────


class TestSubmissionRepository:
    @pytest.mark.asyncio
    async def test_upsert_and_get_submission(self, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        user = await user_repo.create(phone_number="0507777777", first_name="Sub", last_name="", is_active=True, role=UserRole.BASIC_GUARD)
        await db_session.commit()

        week_repo = ScheduleWeekRepository(db_session)
        week = await week_repo.create(
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 7),
            status=WeekStatus.OPEN,
        )
        await db_session.commit()

        repo = SubmissionRepository(db_session)
        data = {
            "general_notes": "Available all week",
            "has_deviation": False,
            "daily_statuses": [
                {
                    "date": date(2026, 6, 1),
                    "is_available": True,
                    "shift_windows": [
                        {
                            "shift_type": ShiftType.MORNING,
                            "start_time": time(6, 0),
                            "end_time": time(14, 0),
                        }
                    ],
                },
                {
                    "date": date(2026, 6, 2),
                    "is_available": True,
                    "shift_windows": [
                        {
                            "shift_type": ShiftType.AFTERNOON,
                            "start_time": time(14, 0),
                            "end_time": time(22, 0),
                        }
                    ],
                },
            ],
        }
        submission = await repo.upsert_submission(user.id, week.id, data)
        await db_session.commit()

        assert submission.id is not None
        assert len(submission.daily_statuses) == 2

        # Fetch it back
        fetched = await repo.get_submission(user.id, week.id)
        assert fetched is not None
        assert fetched.general_notes == "Available all week"
        assert len(fetched.daily_statuses) == 2
        assert len(fetched.daily_statuses[0].shift_windows) == 1

    @pytest.mark.asyncio
    async def test_upsert_replaces_existing(self, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        user = await user_repo.create(phone_number="0508888888", first_name="Rep", last_name="", is_active=True, role=UserRole.BASIC_GUARD)
        await db_session.commit()

        week_repo = ScheduleWeekRepository(db_session)
        week = await week_repo.create(
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 7),
            status=WeekStatus.OPEN,
        )
        await db_session.commit()

        repo = SubmissionRepository(db_session)

        # First submission
        data_v1 = {
            "general_notes": "v1",
            "has_deviation": False,
            "daily_statuses": [
                {
                    "date": date(2026, 6, 1),
                    "is_available": True,
                    "shift_windows": [],
                }
            ],
        }
        await repo.upsert_submission(user.id, week.id, data_v1)
        await db_session.commit()

        # Replace with v2
        data_v2 = {
            "general_notes": "v2",
            "has_deviation": True,
            "daily_statuses": [
                {
                    "date": date(2026, 6, 1),
                    "is_available": False,
                    "shift_windows": [],
                },
                {
                    "date": date(2026, 6, 2),
                    "is_available": True,
                    "shift_windows": [],
                },
            ],
        }
        submission = await repo.upsert_submission(user.id, week.id, data_v2)
        await db_session.commit()

        assert submission.general_notes == "v2"
        assert submission.has_deviation is True
        assert len(submission.daily_statuses) == 2

    @pytest.mark.asyncio
    async def test_get_missing_submissions(self, db_session: AsyncSession):
        user_repo = UserRepository(db_session)
        u1 = await user_repo.create(phone_number="0509000001", first_name="U1", last_name="", is_active=True, role=UserRole.BASIC_GUARD)
        u2 = await user_repo.create(phone_number="0509000002", first_name="U2", last_name="", is_active=True, role=UserRole.BASIC_GUARD)
        u3 = await user_repo.create(phone_number="0509000003", first_name="U3", last_name="", is_active=True, role=UserRole.BASIC_GUARD)
        await db_session.commit()

        week_repo = ScheduleWeekRepository(db_session)
        week = await week_repo.create(
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 7),
            status=WeekStatus.OPEN,
        )
        await db_session.commit()

        repo = SubmissionRepository(db_session)
        # Only u1 submits
        data = {
            "general_notes": None,
            "has_deviation": False,
            "daily_statuses": [
                {"date": date(2026, 6, 1), "is_available": True, "shift_windows": []}
            ],
        }
        await repo.upsert_submission(u1.id, week.id, data)
        await db_session.commit()

        missing = await repo.get_missing_submissions(week.id, [u1.id, u2.id, u3.id])
        assert set(missing) == {u2.id, u3.id}


# ──────────────── AdminRepository ────────────────


class TestAdminRepository:
    @pytest.mark.asyncio
    async def test_create_and_get_by_email(self, db_session: AsyncSession):
        repo = AdminRepository(db_session)
        admin = await repo.create_admin(
            email="admin@test.com",
            password_hash="hashed",
            full_name="Test Admin",
        )
        await db_session.commit()

        found = await repo.get_by_email("admin@test.com")
        assert found is not None
        assert found.full_name == "Test Admin"

    @pytest.mark.asyncio
    async def test_deactivate_admin(self, db_session: AsyncSession):
        repo = AdminRepository(db_session)
        admin = await repo.create_admin(
            email="deac@test.com",
            password_hash="hashed",
            full_name="Deac Admin",
        )
        await db_session.commit()

        deactivated = await repo.deactivate_admin(admin.id)
        assert deactivated.is_active is False


# ──────────────── SystemSettingsRepository ────────────────


class TestSystemSettingsRepository:
    @pytest.mark.asyncio
    async def test_set_and_get(self, db_session: AsyncSession):
        repo = SystemSettingsRepository(db_session)
        await repo.set("reminder_hour", "09:00", "Time to send reminders")
        await db_session.commit()

        value = await repo.get("reminder_hour")
        assert value == "09:00"

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, db_session: AsyncSession):
        repo = SystemSettingsRepository(db_session)
        value = await repo.get("nonexistent_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_set_updates_existing(self, db_session: AsyncSession):
        repo = SystemSettingsRepository(db_session)
        await repo.set("test_key", "v1")
        await db_session.commit()

        await repo.set("test_key", "v2")
        await db_session.commit()

        value = await repo.get("test_key")
        assert value == "v2"

    @pytest.mark.asyncio
    async def test_delete(self, db_session: AsyncSession):
        repo = SystemSettingsRepository(db_session)
        await repo.set("to_delete", "bye")
        await db_session.commit()

        result = await repo.delete("to_delete")
        assert result is True

        value = await repo.get("to_delete")
        assert value is None

        # Delete non-existent
        result = await repo.delete("nonexistent")
        assert result is False