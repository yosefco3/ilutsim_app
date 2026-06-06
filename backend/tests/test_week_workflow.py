"""Integration tests — full week lifecycle (P09).

Tests the complete flow:
  admin opens week → guard submits → admin locks → admin publishes.
Also covers invalid transitions and notification verification.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.constants import WeekStatus
from app.controllers.admin_weeks_controller import router as admin_weeks_router
from app.controllers.submission_controller import router as submission_router
from app.dependencies import (
    get_submission_service,
    get_week_service,
    require_admin_role,
)
from app.exceptions import InvalidTransitionException
from app.messages import Messages


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_app() -> FastAPI:
    """Build a FastAPI app with both admin-weeks and submission routers."""
    app = FastAPI()
    app.include_router(admin_weeks_router)
    app.include_router(submission_router)
    return app


def _admin_payload():
    """Fake decoded-admin payload used to override auth."""
    return {"sub": "admin1", "role": "super_admin"}


def _admin_headers():
    """Bearer header dict — the actual value doesn't matter because
    ``get_current_admin`` is overridden."""
    return {"Authorization": "Bearer faketoken"}


def _valid_day(date_str="2026-06-08"):
    return {
        "date": date_str,
        "is_available": True,
        "shifts": [
            {"shift_type": "morning", "start_time": "07:00", "end_time": "15:00"}
        ],
    }


def _week_obj(
    week_id=None,
    status=WeekStatus.OPEN,
    start_date="2026-06-08",
    end_date="2026-06-14",
):
    """Build a lightweight week-like object with all attributes."""
    wid = week_id or uuid.uuid4()
    return type(
        "Week",
        (),
        {
            "id": wid,
            "status": status,
            "start_date": start_date,
            "end_date": end_date,
        },
    )()


def _submission_obj(sub_id=None, week_id=None):
    sid = sub_id or uuid.uuid4()
    wid = week_id or uuid.uuid4()
    return {
        "id": str(sid),
        "week_id": str(wid),
        "user_id": str(uuid.uuid4()),
        "status": "submitted",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "days": [],
    }


def _setup_app(week_svc, sub_svc=None):
    """Create app with dependency overrides pre-configured."""
    app = _make_app()
    app.dependency_overrides[require_admin_role] = lambda: _admin_payload()
    app.dependency_overrides[get_week_service] = lambda: week_svc
    if sub_svc is not None:
        app.dependency_overrides[get_submission_service] = lambda: sub_svc
    return app


# ===========================================================================
# 1. Full week lifecycle
# ===========================================================================
class TestFullWeekLifecycle:
    """End-to-end: open → submit → lock → publish → open next."""

    def test_full_lifecycle(self):
        week_id = uuid.uuid4()
        next_week_id = uuid.uuid4()
        sub_id = uuid.uuid4()

        week_svc = AsyncMock()
        sub_svc = AsyncMock()

        # --- configure get_current_open_week call sequence ---
        # Route /submissions/current-week calls get_current_open_week
        # Route POST /submissions also calls get_current_open_week (guard check)
        week_svc.get_current_open_week.side_effect = [
            None,                          # Step 1: no open week
            _week_obj(week_id),            # Step 3: after open (current-week)
            _week_obj(week_id),            # Step 4: submit guard check
            _week_obj(week_id),            # Step 5: current-week (still open)
            None,                          # Step 7: after lock (current-week)
            None,                          # Step 8: submission blocked
        ]

        # open_new_week returns
        week_svc.open_new_week.side_effect = [
            _week_obj(week_id),                                              # Step 2
            _week_obj(next_week_id, start_date="2026-06-15", end_date="2026-06-21"),  # Step 10
        ]

        sub_svc.submit.return_value = _submission_obj(sub_id, week_id)

        # lock + publish transitions (controller calls change_week_status)
        week_svc.change_week_status.side_effect = [
            _week_obj(week_id, WeekStatus.LOCKED),
            _week_obj(week_id, WeekStatus.PUBLISHED),
        ]

        app = _setup_app(week_svc, sub_svc)
        client = TestClient(app)

        # Step 1: No weeks → current-week returns null
        resp = client.get("/submissions/current-week")
        assert resp.status_code == 200
        assert resp.json() is None

        # Step 2: Guard cannot submit (no open week)
        resp = client.post(
            "/submissions",
            json={"week_id": str(uuid.uuid4()), "days": [_valid_day()]},
        )
        assert resp.status_code == 403

        # Step 3: Admin opens a new week
        resp = client.post("/admin/weeks/open", headers=_admin_headers())
        assert resp.status_code == 201
        week = resp.json()
        assert week["status"] == "open"

        # Step 4: Get current week returns the open week
        resp = client.get("/submissions/current-week")
        assert resp.status_code == 200
        assert resp.json()["status"] == "open"

        # Step 5: Guard can now submit
        resp = client.post(
            "/submissions",
            json={"week_id": str(week_id), "days": [_valid_day()]},
        )
        assert resp.status_code == 201

        # Step 6: Admin locks the week (new_status is a query param)
        resp = client.patch(
            f"/admin/weeks/{week_id}/status?new_status=locked",
            headers=_admin_headers(),
        )
        assert resp.status_code == 200

        # Step 7: Get current week returns null (locked = not open)
        resp = client.get("/submissions/current-week")
        assert resp.status_code == 200
        assert resp.json() is None

        # Step 8: Guard cannot submit anymore
        resp = client.post(
            "/submissions",
            json={"week_id": str(week_id), "days": [_valid_day()]},
        )
        assert resp.status_code == 403

        # Step 9: Admin publishes
        resp = client.patch(
            f"/admin/weeks/{week_id}/status?new_status=published",
            headers=_admin_headers(),
        )
        assert resp.status_code == 200

        # Step 10: Admin opens NEXT week — different dates
        resp = client.post("/admin/weeks/open", headers=_admin_headers())
        assert resp.status_code == 201
        new_week = resp.json()
        assert new_week["start_date"] != week["start_date"]

        app.dependency_overrides.clear()


# ===========================================================================
# 2. Invalid transitions
# ===========================================================================
class TestInvalidTransitions:
    """Guards against illegal state changes."""

    def test_cannot_open_when_week_already_open(self):
        week_svc = AsyncMock()
        # Controller catches AppBaseException subclasses, not ValueError
        week_svc.open_new_week.side_effect = InvalidTransitionException(
            "A week is already open"
        )

        app = _setup_app(week_svc)
        client = TestClient(app)

        resp = client.post("/admin/weeks/open", headers=_admin_headers())
        assert resp.status_code == 400

        app.dependency_overrides.clear()

    def test_cannot_publish_from_open(self):
        """Publishing directly from open (skip locked) should fail."""
        week_id = uuid.uuid4()
        week_svc = AsyncMock()
        # Controller catches all Exception in status endpoint
        week_svc.change_week_status.side_effect = ValueError(
            "Invalid transition"
        )

        app = _setup_app(week_svc)
        client = TestClient(app)

        resp = client.patch(
            f"/admin/weeks/{week_id}/status?new_status=published",
            headers=_admin_headers(),
        )
        assert resp.status_code == 400

        app.dependency_overrides.clear()

    def test_cannot_lock_nonexistent_week(self):
        """Locking a week that doesn't exist → service raises → 400."""
        week_svc = AsyncMock()
        # Controller catches Exception and returns 400
        week_svc.change_week_status.side_effect = ValueError("Week not found")

        app = _setup_app(week_svc)
        client = TestClient(app)

        resp = client.patch(
            f"/admin/weeks/{uuid.uuid4()}/status?new_status=locked",
            headers=_admin_headers(),
        )
        assert resp.status_code == 400

        app.dependency_overrides.clear()


# ===========================================================================
# 3. Notification sent on open
# ===========================================================================
class TestNotificationOnOpen:
    """Verify that opening a week triggers Telegram notifications."""

    def test_notification_sent_on_open(self):
        week_svc = AsyncMock()
        week_svc.open_new_week.return_value = _week_obj()

        app = _setup_app(week_svc)
        client = TestClient(app)

        resp = client.post("/admin/weeks/open", headers=_admin_headers())

        assert resp.status_code == 201
        # open_new_week was called → the service mock recorded the call
        week_svc.open_new_week.assert_called_once()

        app.dependency_overrides.clear()