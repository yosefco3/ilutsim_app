"""Tests for the automatic Saturday-night (Motzaei Shabbat) week rollover.

The rollover (``WeekService.auto_advance_weeks``) is idempotent and self-healing:
  1. Any OPEN week whose ``start_date`` has arrived is auto-locked (silently —
     no Telegram broadcast at midnight). It is no longer a submission target.
  2. The upcoming Sun–Sat week is ensured CLOSED (existing ``auto_rotate_weeks``)
     so the admin always has a next week ready to open.

A week that was already locked/published, or an OPEN *future* week, is untouched.
"""

import uuid
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.constants import WeekStatus
from app.repositories.schedule_week_repository import ScheduleWeekRepository
from app.services.week_service import WeekService
from app.utils.date_utils import upcoming_sunday, week_range


def _week(status, start, end):
    w = MagicMock()
    w.id = uuid.uuid4()
    w.status = status
    w.start_date = start
    w.end_date = end
    return w


# ── Service-level (mocked repo) ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_lock_expired_open_weeks_locks_silently():
    """An open week whose start_date arrived is locked WITHOUT notifying guards."""
    today = date.today()
    stale = _week(WeekStatus.OPEN, today - timedelta(days=1), today + timedelta(days=5))

    repo = AsyncMock()
    repo.get_open_weeks_started_on_or_before.return_value = [stale]
    repo.get_by_id.return_value = stale
    repo.update.return_value = _week(WeekStatus.LOCKED, stale.start_date, stale.end_date)

    user_repo = AsyncMock()
    svc = WeekService(repo, user_repo)
    await svc.lock_expired_open_weeks()

    # Transitioned to LOCKED…
    repo.update.assert_awaited_once_with(stale.id, status=WeekStatus.LOCKED)
    # …and NO Telegram broadcast happened (user list is only fetched to notify).
    user_repo.get_all.assert_not_awaited()


@pytest.mark.asyncio
async def test_lock_expired_open_weeks_noop_when_none():
    """No stale open week → nothing is locked."""
    repo = AsyncMock()
    repo.get_open_weeks_started_on_or_before.return_value = []

    svc = WeekService(repo)
    await svc.lock_expired_open_weeks()

    repo.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_auto_advance_locks_and_creates_next():
    """auto_advance both locks the stale open week and ensures the upcoming week."""
    today = date.today()
    ws, we = week_range(today)
    stale = _week(WeekStatus.OPEN, today - timedelta(days=1), today + timedelta(days=5))

    repo = AsyncMock()
    repo.get_open_weeks_started_on_or_before.return_value = [stale]
    repo.get_by_id.return_value = stale
    repo.update.return_value = _week(WeekStatus.LOCKED, stale.start_date, stale.end_date)
    repo.get_by_date_range.return_value = None  # upcoming week missing
    repo.save.return_value = _week(WeekStatus.CLOSED, ws, we)
    repo.get_weeks_beyond_retention.return_value = []  # nothing to purge

    svc = WeekService(repo)
    await svc.auto_advance_weeks()

    repo.update.assert_awaited_once_with(stale.id, status=WeekStatus.LOCKED)  # locked
    repo.save.assert_awaited_once()  # upcoming created
    assert repo.save.call_args.args[0].status == WeekStatus.CLOSED


# ── Repository-level (real in-memory DB) ─────────────────────────────────────

@pytest.mark.asyncio
async def test_repo_returns_only_started_open_weeks(db_session):
    """The query filters by status==OPEN AND start_date<=today."""
    from app.models.schedule_week import ScheduleWeek

    today = date.today()
    started = ScheduleWeek(
        start_date=today - timedelta(days=2),
        end_date=today + timedelta(days=4),
        status=WeekStatus.OPEN,
    )
    future = ScheduleWeek(
        start_date=today + timedelta(days=5),
        end_date=today + timedelta(days=11),
        status=WeekStatus.OPEN,
    )
    closed_started = ScheduleWeek(
        start_date=today - timedelta(days=2),
        end_date=today + timedelta(days=4),
        status=WeekStatus.CLOSED,
    )
    db_session.add_all([started, future, closed_started])
    await db_session.commit()

    repo = ScheduleWeekRepository(db_session)
    result = await repo.get_open_weeks_started_on_or_before(today)

    ids = {w.id for w in result}
    assert started.id in ids
    assert future.id not in ids  # open but still in the future
    assert closed_started.id not in ids  # started but not open


# ── Full flow (service + real DB) ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_full_rollover_locks_open_and_creates_upcoming(db_session):
    """End-to-end: a started open week is locked; a future open week survives;
    the upcoming CLOSED week is created."""
    from app.models.schedule_week import ScheduleWeek

    today = date.today()
    # Open week whose start_date has arrived → must be locked.
    started_open = ScheduleWeek(
        start_date=today - timedelta(days=1),
        end_date=today + timedelta(days=5),
        status=WeekStatus.OPEN,
    )
    # Open week far in the future → must stay OPEN (admin's manual flow).
    far_start = upcoming_sunday(today) + timedelta(days=14)
    future_open = ScheduleWeek(
        start_date=far_start,
        end_date=far_start + timedelta(days=6),
        status=WeekStatus.OPEN,
    )
    db_session.add_all([started_open, future_open])
    await db_session.commit()

    repo = ScheduleWeekRepository(db_session)
    svc = WeekService(repo)  # no user_repo → no notifications regardless
    await svc.auto_advance_weeks()

    await db_session.refresh(started_open)
    await db_session.refresh(future_open)
    assert started_open.status == WeekStatus.LOCKED
    assert future_open.status == WeekStatus.OPEN

    # Upcoming Sun–Sat week now exists as CLOSED.
    ws, we = week_range(today)
    upcoming = await repo.get_by_date_range(ws, we)
    assert upcoming is not None
    assert upcoming.status == WeekStatus.CLOSED
