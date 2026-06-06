"""Tests for week-status transition validation (P03).

Validates that change_week_status only allows:
  open → locked → published
  locked → open  (admin can reopen a locked week)
and rejects all illegal transitions with AppBaseException(400).
"""

import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.constants import WeekStatus
from app.exceptions import AppBaseException
from app.services.week_service import WeekService


# ── helpers ────────────────────────────────────────────────────────────


def _mock_week(status: WeekStatus) -> MagicMock:
    """Create a week-like MagicMock."""
    w = MagicMock()
    w.id = uuid.uuid4()
    w.start_date = date(2025, 6, 1)
    w.end_date = date(2025, 6, 7)
    w.status = status
    return w


def _svc(week) -> WeekService:
    """Return a WeekService with a mock repo returning *week* on get_by_id."""
    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = week
    mock_repo.update.return_value = week
    return WeekService(mock_repo)


# ── tests ──────────────────────────────────────────────────────────────


class TestValidTransitions:
    """Happy-path transitions that should succeed."""

    @pytest.mark.asyncio
    async def test_open_to_locked(self):
        week = _mock_week(WeekStatus.OPEN)
        svc = _svc(week)

        result = await svc.change_week_status(week.id, WeekStatus.LOCKED)
        assert result.status == WeekStatus.LOCKED

    @pytest.mark.asyncio
    async def test_locked_to_published(self):
        week = _mock_week(WeekStatus.LOCKED)
        svc = _svc(week)

        result = await svc.change_week_status(week.id, WeekStatus.PUBLISHED)
        assert result.status == WeekStatus.PUBLISHED

    @pytest.mark.asyncio
    async def test_locked_to_open(self):
        """Admin can reopen a locked week."""
        week = _mock_week(WeekStatus.LOCKED)
        svc = _svc(week)

        result = await svc.change_week_status(week.id, WeekStatus.OPEN)
        assert result.status == WeekStatus.OPEN


class TestInvalidTransitions:
    """Illegal transitions that must raise AppBaseException."""

    @pytest.mark.asyncio
    async def test_open_to_published_rejected(self):
        week = _mock_week(WeekStatus.OPEN)
        svc = _svc(week)

        with pytest.raises(AppBaseException) as exc_info:
            await svc.change_week_status(week.id, WeekStatus.PUBLISHED)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_published_to_open_rejected(self):
        week = _mock_week(WeekStatus.PUBLISHED)
        svc = _svc(week)

        with pytest.raises(AppBaseException) as exc_info:
            await svc.change_week_status(week.id, WeekStatus.OPEN)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_same_status_open_rejected(self):
        """No-op transition open → open is rejected."""
        week = _mock_week(WeekStatus.OPEN)
        svc = _svc(week)

        with pytest.raises(AppBaseException) as exc_info:
            await svc.change_week_status(week.id, WeekStatus.OPEN)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_same_status_locked_rejected(self):
        """No-op transition locked → locked is rejected."""
        week = _mock_week(WeekStatus.LOCKED)
        svc = _svc(week)

        with pytest.raises(AppBaseException) as exc_info:
            await svc.change_week_status(week.id, WeekStatus.LOCKED)
        assert exc_info.value.status_code == 400
