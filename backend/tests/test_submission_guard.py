"""Tests for submission status guard — P05."""

import uuid
from unittest.mock import AsyncMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.controllers.submission_controller import router as submission_router
from app.dependencies import get_week_service, get_submission_service
from datetime import datetime, timezone

from app.messages import Messages


def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(submission_router)
    return app


def _valid_day(date_str="2025-06-01"):
    return {
        "date": date_str,
        "is_available": True,
        "shifts": [{"shift_type": "morning", "start_time": "07:00", "end_time": "15:00"}],
    }


class TestSubmissionStatusGuard:
    """POST /submissions is blocked when week is not open."""

    def test_submit_when_open_week_success(self):
        """Open week → submission accepted (201)."""
        week_id = uuid.uuid4()

        week_svc = AsyncMock()
        week_svc.get_current_open_week.return_value = type(
            "Week", (), {"id": week_id}
        )()

        sub_svc = AsyncMock()
        sub_svc.submit.return_value = {
            "id": str(uuid.uuid4()),
            "week_id": str(week_id),
            "user_id": str(uuid.uuid4()),
            "status": "submitted",
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "days": [],
        }

        app = _make_app()
        app.dependency_overrides[get_week_service] = lambda: week_svc
        app.dependency_overrides[get_submission_service] = lambda: sub_svc
        client = TestClient(app)

        resp = client.post(
            "/submissions",
            json={"week_id": str(week_id), "days": [_valid_day()]},
        )
        assert resp.status_code == 201
        app.dependency_overrides.clear()

    def test_submit_when_no_open_week_403(self):
        """No open week → 403 with SUBMISSION_CLOSED message."""
        sub_svc = AsyncMock()
        week_svc = AsyncMock()
        week_svc.get_current_open_week.return_value = None

        app = _make_app()
        app.dependency_overrides[get_week_service] = lambda: week_svc
        app.dependency_overrides[get_submission_service] = lambda: sub_svc
        client = TestClient(app)

        resp = client.post(
            "/submissions",
            json={"week_id": str(uuid.uuid4()), "days": [_valid_day()]},
        )
        assert resp.status_code == 403
        assert Messages.SUBMISSION_CLOSED in resp.json()["detail"]
        app.dependency_overrides.clear()

    def test_submit_wrong_week_id_403(self):
        """Open week exists but week_id doesn't match → 403."""
        real_week_id = uuid.uuid4()
        wrong_week_id = uuid.uuid4()

        week_svc = AsyncMock()
        week_svc.get_current_open_week.return_value = type(
            "Week", (), {"id": real_week_id}
        )()

        sub_svc = AsyncMock()

        app = _make_app()
        app.dependency_overrides[get_week_service] = lambda: week_svc
        app.dependency_overrides[get_submission_service] = lambda: sub_svc
        client = TestClient(app)

        resp = client.post(
            "/submissions",
            json={"week_id": str(wrong_week_id), "days": [_valid_day()]},
        )
        assert resp.status_code == 403
        assert Messages.SUBMISSION_WRONG_WEEK in resp.json()["detail"]
        app.dependency_overrides.clear()

    def test_get_submissions_always_allowed(self):
        """GET /submissions/user/{id} works regardless of week status."""
        sub_svc = AsyncMock()
        sub_svc.get_submissions_for_user.return_value = []

        week_svc = AsyncMock()

        app = _make_app()
        app.dependency_overrides[get_week_service] = lambda: week_svc
        app.dependency_overrides[get_submission_service] = lambda: sub_svc
        client = TestClient(app)

        resp = client.get(f"/submissions/user/{uuid.uuid4()}")
        assert resp.status_code == 200
        app.dependency_overrides.clear()