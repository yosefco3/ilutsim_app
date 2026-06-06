"""
Tests for POST /admin/weeks/open endpoint (P02).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date

from fastapi.testclient import TestClient

import uuid

from app.constants import WeekStatus
from app.exceptions import ConflictException
from app.main import create_app
from app.utils.date_utils import week_range


# ── Service-level unit tests ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_open_new_week_success():
    """When no open week exists, creates and returns a new open week."""
    from app.services.week_service import WeekService

    mock_repo = AsyncMock()
    mock_repo.get_current_open_week.return_value = None

    saved_week = MagicMock()
    saved_week.id = uuid.uuid4()
    saved_week.start_date = date(2025, 6, 15)
    saved_week.end_date = date(2025, 6, 21)
    saved_week.status = WeekStatus.OPEN
    mock_repo.create.return_value = saved_week

    svc = WeekService(mock_repo)
    result = await svc.open_new_week(date(2025, 6, 15))

    assert result.status == WeekStatus.OPEN
    mock_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_open_new_week_conflict():
    """When an open week already exists, raises ConflictException."""
    from app.services.week_service import WeekService

    mock_repo = AsyncMock()
    mock_repo.get_current_open_week.return_value = MagicMock()

    svc = WeekService(mock_repo)

    with pytest.raises(ConflictException):
        await svc.open_new_week()


@pytest.mark.asyncio
async def test_open_new_week_uses_week_range():
    """Week start/end should be computed via week_range."""
    from app.services.week_service import WeekService

    mock_repo = AsyncMock()
    mock_repo.get_current_open_week.return_value = None

    created = MagicMock()
    created.id = uuid.uuid4()
    ws, we = week_range(date(2025, 6, 18))
    created.start_date = ws
    created.end_date = we
    created.status = WeekStatus.OPEN
    mock_repo.create.return_value = created

    svc = WeekService(mock_repo)
    result = await svc.open_new_week(date(2025, 6, 18))

    assert result.start_date == date(2025, 6, 22)
    assert result.end_date == date(2025, 6, 28)


# ── API integration tests (sync TestClient) ──────────────────────────────

_mock_admin_payload = {"role": "admin", "user_id": "test-admin"}


def test_api_open_week_201():
    """POST /admin/weeks/open returns 201 when no open week exists."""
    from app.dependencies import get_week_service, require_admin_role
    from app.schemas.week_schemas import WeekResponse

    app = create_app()

    svc = AsyncMock()
    svc.open_new_week.return_value = WeekResponse(
        id=uuid.uuid4(),
        start_date=date(2025, 6, 15),
        end_date=date(2025, 6, 21),
        status=WeekStatus.OPEN,
    )

    app.dependency_overrides[require_admin_role] = lambda: _mock_admin_payload
    app.dependency_overrides[get_week_service] = lambda: svc
    client = TestClient(app)

    try:
        resp = client.post("/admin/weeks/open")
        assert resp.status_code == 201
        body = resp.json()
        assert body["status"] == "open"
    finally:
        app.dependency_overrides.clear()


def test_api_open_week_conflict_409():
    """POST /admin/weeks/open returns 409 when an open week already exists."""
    from app.dependencies import get_week_service, require_admin_role

    app = create_app()

    svc = AsyncMock()
    svc.open_new_week.side_effect = ConflictException("already open")

    app.dependency_overrides[require_admin_role] = lambda: _mock_admin_payload
    app.dependency_overrides[get_week_service] = lambda: svc
    client = TestClient(app)

    try:
        resp = client.post("/admin/weeks/open")
        assert resp.status_code == 409
    finally:
        app.dependency_overrides.clear()