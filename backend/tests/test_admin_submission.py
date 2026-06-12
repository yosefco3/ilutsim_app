"""Tests for admin-filled submissions — POST /submissions/admin.

An admin fills constraints on behalf of a guard who has no Telegram. Unlike the
guard endpoint, this works regardless of week status (override_lock=True).
"""

import uuid
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.controllers.submission_controller import router as submission_router
from app.dependencies import (
    get_week_service,
    get_submission_service,
    require_admin_role,
)


def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(submission_router)
    return app


def _valid_day(day_index=0):
    return {
        "day_index": day_index,
        "shifts": [{"shift_type": "morning", "from_hour": "07:00", "to_hour": "15:00"}],
    }


def _fake_submission(week_id, user_id):
    return {
        "id": str(uuid.uuid4()),
        "week_id": str(week_id),
        "user_id": str(user_id),
        "general_notes": None,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "days": [],
    }


class TestAdminSubmission:
    """POST /submissions/admin lets an admin submit for a guard."""

    def test_admin_submit_success_overrides_lock(self):
        """Admin submission succeeds and calls create_submission with override_lock=True."""
        week_id = uuid.uuid4()
        user_id = uuid.uuid4()
        week_start = date(2025, 6, 1)

        week_svc = AsyncMock()
        week_svc.get_week.return_value = type(
            "Week", (), {"id": week_id, "start_date": week_start}
        )()

        sub_svc = AsyncMock()
        sub_svc.create_submission.return_value = _fake_submission(week_id, user_id)

        app = _make_app()
        app.dependency_overrides[get_week_service] = lambda: week_svc
        app.dependency_overrides[get_submission_service] = lambda: sub_svc
        app.dependency_overrides[require_admin_role] = lambda: None
        client = TestClient(app)

        resp = client.post(
            "/submissions/admin",
            json={
                "user_id": str(user_id),
                "week_id": str(week_id),
                "days": [_valid_day()],
            },
        )
        assert resp.status_code == 201, f"Got {resp.status_code}: {resp.text}"

        # override_lock must be True so closed/locked weeks are allowed
        _, kwargs = sub_svc.create_submission.call_args
        assert kwargs.get("override_lock") is True

        # The submission must target the explicit guard user_id
        created = sub_svc.create_submission.call_args[0][0]
        assert str(created.user_id) == str(user_id)
        app.dependency_overrides.clear()

    def test_admin_get_submission_returns_existing(self):
        """GET /submissions/admin returns the guard's existing submission for edit."""
        week_id = uuid.uuid4()
        user_id = uuid.uuid4()

        sub_svc = AsyncMock()
        sub_svc.get_submission.return_value = _fake_submission(week_id, user_id)
        week_svc = AsyncMock()

        app = _make_app()
        app.dependency_overrides[get_week_service] = lambda: week_svc
        app.dependency_overrides[get_submission_service] = lambda: sub_svc
        app.dependency_overrides[require_admin_role] = lambda: None
        client = TestClient(app)

        resp = client.get(
            "/submissions/admin",
            params={"user_id": str(user_id), "week_id": str(week_id)},
        )
        assert resp.status_code == 200, f"Got {resp.status_code}: {resp.text}"
        sub_svc.get_submission.assert_awaited_once()
        app.dependency_overrides.clear()

    def test_admin_get_submission_null_when_none(self):
        """GET /submissions/admin returns null when the guard hasn't submitted."""
        sub_svc = AsyncMock()
        sub_svc.get_submission.return_value = None
        week_svc = AsyncMock()

        app = _make_app()
        app.dependency_overrides[get_week_service] = lambda: week_svc
        app.dependency_overrides[get_submission_service] = lambda: sub_svc
        app.dependency_overrides[require_admin_role] = lambda: None
        client = TestClient(app)

        resp = client.get(
            "/submissions/admin",
            params={"user_id": str(uuid.uuid4()), "week_id": str(uuid.uuid4())},
        )
        assert resp.status_code == 200
        assert resp.json() is None
        app.dependency_overrides.clear()

    def test_admin_submit_requires_user_id(self):
        """Missing user_id → 422 validation error."""
        week_id = uuid.uuid4()
        week_svc = AsyncMock()
        sub_svc = AsyncMock()

        app = _make_app()
        app.dependency_overrides[get_week_service] = lambda: week_svc
        app.dependency_overrides[get_submission_service] = lambda: sub_svc
        app.dependency_overrides[require_admin_role] = lambda: None
        client = TestClient(app)

        resp = client.post(
            "/submissions/admin",
            json={"week_id": str(week_id), "days": [_valid_day()]},
        )
        assert resp.status_code == 422
        app.dependency_overrides.clear()
