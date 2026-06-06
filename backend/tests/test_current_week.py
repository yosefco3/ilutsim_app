"""Tests for GET /submissions/current-week endpoint (P04)."""

import uuid
from datetime import date
from unittest.mock import AsyncMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.controllers.submission_controller import router as submission_router
from app.dependencies import get_week_service


def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(submission_router)
    return app


class TestGetCurrentWeek:
    """Tests for GET /submissions/current-week."""

    def test_get_current_week_open(self):
        """Returns the open week data."""
        week_id = str(uuid.uuid4())
        mock_svc = AsyncMock()
        mock_svc.get_current_open_week.return_value = {
            "id": week_id,
            "start_date": date(2025, 1, 6),
            "end_date": date(2025, 1, 12),
            "status": "open",
        }

        app = _make_app()
        app.dependency_overrides[get_week_service] = lambda: mock_svc
        client = TestClient(app)

        resp = client.get("/submissions/current-week")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == week_id
        assert data["status"] == "open"
        assert data["start_date"] == "2025-01-06"
        assert data["end_date"] == "2025-01-12"
        app.dependency_overrides.clear()

    def test_get_current_week_none_when_locked(self):
        """Returns null when week is locked."""
        mock_svc = AsyncMock()
        mock_svc.get_current_open_week.return_value = None

        app = _make_app()
        app.dependency_overrides[get_week_service] = lambda: mock_svc
        client = TestClient(app)

        resp = client.get("/submissions/current-week")
        assert resp.status_code == 200
        assert resp.json() is None
        app.dependency_overrides.clear()

    def test_get_current_week_none_when_no_weeks(self):
        """Returns null when no weeks exist."""
        mock_svc = AsyncMock()
        mock_svc.get_current_open_week.return_value = None

        app = _make_app()
        app.dependency_overrides[get_week_service] = lambda: mock_svc
        client = TestClient(app)

        resp = client.get("/submissions/current-week")
        assert resp.status_code == 200
        assert resp.json() is None
        app.dependency_overrides.clear()

    def test_get_current_week_none_when_published(self):
        """Returns null when week is published (not open)."""
        mock_svc = AsyncMock()
        mock_svc.get_current_open_week.return_value = None

        app = _make_app()
        app.dependency_overrides[get_week_service] = lambda: mock_svc
        client = TestClient(app)

        resp = client.get("/submissions/current-week")
        assert resp.status_code == 200
        assert resp.json() is None
        app.dependency_overrides.clear()