"""
Tests for Excel export service and controller.
"""

import io
import json
import uuid
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.constants import EventType, ShiftType, SubmissionStatus, WeekStatus
from app.messages import Messages
from app.services.excel_export_service import ExcelExportService


# ── Helpers ──────────────────────────────────────────────────────────


def _make_user(user_id=None, full_name="Test Guard", phone="0501234567"):
    user = MagicMock()
    user.id = user_id or uuid.uuid4()
    user.full_name = full_name
    user.phone_number = phone
    user.is_active = True
    return user


def _make_week(week_id=None, week_start=None):
    week = MagicMock()
    week.id = week_id or uuid.uuid4()
    week.week_start = week_start or date(2025, 1, 5)  # Sunday
    week.week_end = week.week_start + timedelta(days=6)
    week.status = WeekStatus.OPEN
    return week


def _make_submission(user_id, week_id, constraints=None, status=SubmissionStatus.SUBMITTED):
    sub = MagicMock()
    sub.id = uuid.uuid4()
    sub.user_id = user_id
    sub.week_id = week_id
    sub.status = status
    sub.constraints = constraints
    return sub


def _make_event(user_id, event_type=EventType.VACATION, start=None, end=None):
    ev = MagicMock()
    ev.id = uuid.uuid4()
    ev.user_id = user_id
    ev.event_type = event_type
    ev.start_date = start or date(2025, 1, 5)
    ev.end_date = end or date(2025, 1, 7)
    ev.notes = ""
    return ev


def _create_service(
    week=None,
    users=None,
    submissions=None,
    events=None,
):
    """Build an ExcelExportService with mocked repos."""
    sub_repo = AsyncMock()
    user_repo = AsyncMock()
    week_repo = AsyncMock()
    event_repo = AsyncMock()

    week_repo.get_by_id.return_value = week
    user_repo.get_active_users.return_value = users or []
    sub_repo.get_by_week.return_value = submissions or []
    sub_repo.get_by_user.return_value = submissions or []
    event_repo.get_by_user.return_value = events or []
    user_repo.get_by_id.return_value = users[0] if users else None

    return ExcelExportService(
        submission_repo=sub_repo,
        user_repo=user_repo,
        week_repo=week_repo,
        event_repo=event_repo,
    )


# ── Weekly schedule export tests ────────────────────────────────────


@pytest.mark.asyncio
async def test_export_weekly_schedule_basic():
    """Basic weekly schedule export with one user and submission."""
    user = _make_user()
    week = _make_week()
    constraints = {
        str(week.week_start): {"available": True, "shifts": ["morning"]},
        str(week.week_start + timedelta(days=1)): {"available": False, "shifts": []},
    }
    sub = _make_submission(user.id, week.id, json.dumps(constraints))

    svc = _create_service(week=week, users=[user], submissions=[sub])

    with patch("app.services.excel_export_service.HAS_OPENPYXL", True):
        data = await svc.export_weekly_schedule(week.id)

    assert isinstance(data, bytes)
    assert len(data) > 0

    # Verify it's a valid Excel (ZIP magic bytes)
    assert data[:2] == b"PK"


@pytest.mark.asyncio
async def test_export_weekly_no_submission_auto_absence():
    """Users without submissions get auto-absence markers."""
    user = _make_user()
    week = _make_week()

    svc = _create_service(week=week, users=[user], submissions=[])

    with patch("app.services.excel_export_service.HAS_OPENPYXL", True):
        data = await svc.export_weekly_schedule(week.id)

    assert isinstance(data, bytes)
    assert data[:2] == b"PK"


@pytest.mark.asyncio
async def test_export_weekly_with_event():
    """Events overlapping the week are shown in cells."""
    user = _make_user()
    week = _make_week()
    sub = _make_submission(user.id, week.id, "{}")
    event = _make_event(user.id, start=week.week_start, end=week.week_start + timedelta(days=1))

    svc = _create_service(week=week, users=[user], submissions=[sub], events=[event])

    with patch("app.services.excel_export_service.HAS_OPENPYXL", True):
        data = await svc.export_weekly_schedule(week.id)

    assert isinstance(data, bytes)
    assert data[:2] == b"PK"


@pytest.mark.asyncio
async def test_export_weekly_week_not_found():
    """Raises ValueError for unknown week ID."""
    svc = _create_service()

    with pytest.raises(ValueError, match="not found"):
        await svc.export_weekly_schedule(uuid.uuid4())


@pytest.mark.asyncio
async def test_export_weekly_no_openpyxl():
    """Raises RuntimeError when openpyxl is not installed."""
    svc = _create_service(week=_make_week())

    with patch("app.services.excel_export_service.HAS_OPENPYXL", False):
        with pytest.raises(RuntimeError, match="openpyxl"):
            await svc.export_weekly_schedule(svc._week_repo.get_by_id.return_value.id)


# ── Deviation report tests ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_export_deviation_report_basic():
    """Deviation report with one guard below threshold."""
    user = _make_user()
    week = _make_week()
    # Only 1 shift (below threshold of 3)
    constraints = {
        str(week.week_start): {"available": True, "shifts": ["morning"]},
    }
    sub = _make_submission(user.id, week.id, json.dumps(constraints))

    svc = _create_service(week=week, users=[user], submissions=[sub])

    with patch("app.services.excel_export_service.HAS_OPENPYXL", True):
        data = await svc.export_deviation_report(week.id)

    assert isinstance(data, bytes)
    assert data[:2] == b"PK"


@pytest.mark.asyncio
async def test_export_deviation_missing_submission():
    """Guards with no submission are shown in deviation report."""
    user = _make_user()
    week = _make_week()

    svc = _create_service(week=week, users=[user], submissions=[])

    with patch("app.services.excel_export_service.HAS_OPENPYXL", True):
        data = await svc.export_deviation_report(week.id)

    assert isinstance(data, bytes)


@pytest.mark.asyncio
async def test_export_deviation_week_not_found():
    """Raises ValueError for unknown week ID."""
    svc = _create_service()

    with pytest.raises(ValueError, match="not found"):
        await svc.export_deviation_report(uuid.uuid4())


# ── Guard history report tests ──────────────────────────────────────


@pytest.mark.asyncio
async def test_export_guard_history_basic():
    """Guard history report across a date range."""
    user = _make_user()
    start = date(2025, 1, 5)
    end = date(2025, 1, 19)  # 2 weeks

    svc = _create_service(users=[user], submissions=[])

    with patch("app.services.excel_export_service.HAS_OPENPYXL", True):
        data = await svc.export_guard_history(user.id, start, end)

    assert isinstance(data, bytes)
    assert data[:2] == b"PK"


@pytest.mark.asyncio
async def test_export_guard_history_with_events():
    """Guard history includes events overlapping the date range."""
    user = _make_user()
    start = date(2025, 1, 5)
    end = date(2025, 1, 19)
    event = _make_event(user.id, start=date(2025, 1, 6), end=date(2025, 1, 8))

    svc = _create_service(users=[user], submissions=[], events=[event])

    with patch("app.services.excel_export_service.HAS_OPENPYXL", True):
        data = await svc.export_guard_history(user.id, start, end)

    assert isinstance(data, bytes)


@pytest.mark.asyncio
async def test_export_guard_history_user_not_found():
    """Raises ValueError for unknown user ID."""
    svc = _create_service(users=[])

    with pytest.raises(ValueError, match="not found"):
        await svc.export_guard_history(uuid.uuid4(), date(2025, 1, 5), date(2025, 1, 19))


# ── Integration: verify Excel content via openpyxl ───────────────────


@pytest.mark.asyncio
async def test_weekly_excel_has_correct_structure():
    """Verify the generated Excel has correct title and header rows."""
    try:
        import openpyxl
    except ImportError:
        pytest.skip("openpyxl not installed")

    user = _make_user(full_name="יוסי כהן")
    week = _make_week(week_start=date(2025, 1, 5))
    constraints = {
        str(week.week_start): {"available": True, "shifts": ["morning", "afternoon"]},
    }
    sub = _make_submission(user.id, week.id, json.dumps(constraints))

    svc = _create_service(week=week, users=[user], submissions=[sub])

    with patch("app.services.excel_export_service.HAS_OPENPYXL", True):
        data = await svc.export_weekly_schedule(week.id)

    wb = openpyxl.load_workbook(io.BytesIO(data))
    ws = wb.active

    # Title row
    assert ws.cell(row=1, column=1).value is not None

    # Header row (row 3)
    assert ws.cell(row=3, column=1).value == Messages.EXCEL_HEADER_NAME
    assert ws.cell(row=3, column=2).value == "ראשון"

    # Data row (row 4) - user name
    assert ws.cell(row=4, column=1).value == "יוסי כהן"


@pytest.mark.asyncio
async def test_deviation_excel_has_correct_data():
    """Verify deviation Excel shows guards below threshold."""
    try:
        import openpyxl
    except ImportError:
        pytest.skip("openpyxl not installed")

    user = _make_user(full_name="דני לוי", phone="0509876543")
    week = _make_week()
    constraints = {
        str(week.week_start): {"available": True, "shifts": ["morning"]},
    }
    sub = _make_submission(user.id, week.id, json.dumps(constraints))

    svc = _create_service(week=week, users=[user], submissions=[sub])

    with patch("app.services.excel_export_service.HAS_OPENPYXL", True):
        data = await svc.export_deviation_report(week.id)

    wb = openpyxl.load_workbook(io.BytesIO(data))
    ws = wb.active

    # Header row
    assert ws.cell(row=3, column=1).value == Messages.EXCEL_HEADER_NAME

    # Data row - should have user with only 1 shift (below threshold=3)
    assert ws.cell(row=4, column=1).value == "דני לוי"
    assert ws.cell(row=4, column=3).value == "1"  # shift count
    assert ws.cell(row=4, column=5).value == "2-"  # deviation (3-1=2 below)