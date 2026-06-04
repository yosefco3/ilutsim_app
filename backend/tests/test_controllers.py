"""
Tests for STEP 05 — Controllers.

Uses FastAPI TestClient with dependency overrides to test router endpoints
without touching the database.
"""

import uuid
from unittest.mock import ANY, AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.controllers.auth_controller import router as auth_router
from app.controllers.submission_controller import router as submission_router
from app.controllers.admin_users_controller import router as admin_users_router
from app.controllers.admin_weeks_controller import router as admin_weeks_router
from app.controllers.admin_events_controller import router as admin_events_router
from app.controllers.admin_notifications_controller import router as admin_notif_router
from app.controllers.admin_export_controller import router as admin_export_router
from app.controllers.admin_settings_controller import router as admin_settings_router
from app.controllers.admin_admins_controller import router as admin_admins_router
from app.dependencies import (
    get_auth_service,
    get_current_admin,
    get_submission_service,
    get_user_service,
    get_week_service,
    require_admin_role,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_app() -> FastAPI:
    """Create a test FastAPI app with all routers."""
    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(submission_router)
    app.include_router(admin_users_router)
    app.include_router(admin_weeks_router)
    app.include_router(admin_events_router)
    app.include_router(admin_notif_router)
    app.include_router(admin_export_router)
    app.include_router(admin_settings_router)
    app.include_router(admin_admins_router)
    return app


def _mock_admin_payload():
    """Dependency override that always passes admin check."""
    return {"user_id": "admin-123", "telegram_id": 999, "role": "admin"}


# ---------------------------------------------------------------------------
# Auth Controller Tests
# ---------------------------------------------------------------------------

class TestAuthController:
    """Tests for /auth endpoints."""

    def test_telegram_login_missing_init_data(self):
        """Empty body hits the `if not body.init_data` guard -> 400."""
        app = _make_app()
        client = TestClient(app)
        resp = client.post("/auth/telegram", json={})
        assert resp.status_code == 400

    @patch("app.controllers.auth_controller.get_telegram_user_id")
    def test_telegram_login_success(self, mock_parse):
        mock_parse.return_value = 123456

        mock_svc = AsyncMock()
        mock_svc.login_with_telegram.return_value = "jwt-token-abc"

        app = _make_app()
        app.dependency_overrides[get_auth_service] = lambda: mock_svc
        client = TestClient(app)

        resp = client.post(
            "/auth/telegram",
            json={"init_data": "user=%7B%22id%22%3A123456%7D&hash=abc123"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert data["token"] == "jwt-token-abc"
        mock_parse.assert_called_once_with(
            "user=%7B%22id%22%3A123456%7D&hash=abc123",
            ANY,  # bot_token from settings
        )
        mock_svc.login_with_telegram.assert_called_once_with(123456)
        app.dependency_overrides.clear()

    def test_me_success(self):
        mock_admin = {"sub": "admin-1", "username": "admin", "role": "admin"}

        app = _make_app()
        app.dependency_overrides[get_current_admin] = lambda: mock_admin
        client = TestClient(app)

        resp = client.get("/auth/me")
        assert resp.status_code == 200
        assert resp.json()["username"] == "admin"
        assert resp.json()["role"] == "admin"
        app.dependency_overrides.clear()

    def test_me_unauthorized(self):
        """Without auth override, /auth/me should return 401/403."""
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/auth/me")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Submission Controller Tests
# ---------------------------------------------------------------------------

class TestSubmissionController:
    """Tests for /submissions endpoints."""

    def test_get_current_week_no_data(self):
        """GET /submissions/current-week returns 404 when no active week."""
        mock_svc = AsyncMock()
        mock_svc.get_current_open_week.return_value = None

        app = _make_app()
        app.dependency_overrides[get_week_service] = lambda: mock_svc
        client = TestClient(app)

        resp = client.get("/submissions/current-week")
        assert resp.status_code == 404
        app.dependency_overrides.clear()

    def test_get_current_week_success(self):
        """GET /submissions/current-week returns data when available."""
        from datetime import date

        mock_svc = AsyncMock()
        mock_svc.get_current_open_week.return_value = {
            "id": str(uuid.uuid4()),
            "start_date": date(2025, 1, 6),
            "end_date": date(2025, 1, 12),
            "deadline": "2025-01-05T20:00:00",
            "status": "open",
            "is_locked": False,
        }

        app = _make_app()
        app.dependency_overrides[get_week_service] = lambda: mock_svc
        client = TestClient(app)

        resp = client.get("/submissions/current-week")
        assert resp.status_code == 200
        app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Admin Users Controller Tests
# ---------------------------------------------------------------------------

class TestAdminUsersController:
    """Tests for /admin/users endpoints."""

    def test_list_users_requires_admin(self):
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/admin/users")
        assert resp.status_code in (401, 403)

    def test_list_users_success(self):
        mock_svc = AsyncMock()
        mock_svc.get_active_users.return_value = []

        app = _make_app()
        app.dependency_overrides[require_admin_role] = _mock_admin_payload
        app.dependency_overrides[get_user_service] = lambda: mock_svc
        client = TestClient(app)

        resp = client.get("/admin/users")
        assert resp.status_code == 200
        app.dependency_overrides.clear()

    def test_get_user_not_found(self):
        mock_svc = AsyncMock()
        mock_svc.get_user.return_value = None

        app = _make_app()
        app.dependency_overrides[require_admin_role] = _mock_admin_payload
        app.dependency_overrides[get_user_service] = lambda: mock_svc
        client = TestClient(app)

        fake_id = str(uuid.uuid4())
        resp = client.get(f"/admin/users/{fake_id}")
        assert resp.status_code == 404
        app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Admin Weeks Controller Tests
# ---------------------------------------------------------------------------

class TestAdminWeeksController:
    """Tests for /admin/weeks endpoints."""

    def test_list_weeks_requires_admin(self):
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/admin/weeks")
        assert resp.status_code in (401, 403)

    def test_create_week_requires_admin(self):
        app = _make_app()
        client = TestClient(app)
        resp = client.post(
            "/admin/weeks",
            json={"start_date": "2025-01-06", "end_date": "2025-01-12"},
        )
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Admin Events Controller Tests
# ---------------------------------------------------------------------------

class TestAdminEventsController:
    """Tests for /admin/events endpoints."""

    def test_create_event_requires_admin(self):
        app = _make_app()
        client = TestClient(app)
        resp = client.post(
            "/admin/events",
            json={"week_id": str(uuid.uuid4()), "event_type": "SHIFT"},
        )
        assert resp.status_code in (401, 403)

    def test_get_events_for_week_requires_admin(self):
        app = _make_app()
        client = TestClient(app)
        fake_id = str(uuid.uuid4())
        resp = client.get(f"/admin/events/week/{fake_id}")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Admin Notifications Controller Tests
# ---------------------------------------------------------------------------

class TestAdminNotificationsController:
    """Tests for /admin/notifications endpoints."""

    def test_remind_requires_admin(self):
        app = _make_app()
        client = TestClient(app)
        fake_id = str(uuid.uuid4())
        resp = client.post(f"/admin/notifications/remind/{fake_id}")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Admin Export Controller Tests
# ---------------------------------------------------------------------------

class TestAdminExportController:
    """Tests for /admin/export endpoints."""

    def test_export_requires_admin(self):
        app = _make_app()
        client = TestClient(app)
        fake_id = str(uuid.uuid4())
        resp = client.get(f"/admin/export/week/{fake_id}")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Admin Settings Controller Tests
# ---------------------------------------------------------------------------

class TestAdminSettingsController:
    """Tests for /admin/settings endpoints."""

    def test_get_settings_requires_admin(self):
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/admin/settings")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Admin Admins Controller Tests
# ---------------------------------------------------------------------------

class TestAdminAdminsController:
    """Tests for /admin/admins endpoints."""

    def test_list_admins_requires_admin(self):
        app = _make_app()
        client = TestClient(app)
        resp = client.get("/admin/admins")
        assert resp.status_code in (401, 403)

    def test_create_admin_requires_admin(self):
        app = _make_app()
        client = TestClient(app)
        resp = client.post(
            "/admin/admins",
            params={"telegram_id": 123, "display_name": "Test Admin"},
        )
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Route Registration Test
# ---------------------------------------------------------------------------

class TestRouteRegistration:
    """Verify all expected routes are registered in main.py."""

    def test_main_app_has_routes(self):
        from app.main import app
        routes = [r.path for r in app.routes]
        assert "/health" in routes
        assert "/auth/telegram" in routes
        assert "/auth/me" in routes
        assert "/submissions/current-week" in routes
        assert "/admin/users" in routes
        assert "/admin/weeks" in routes
        assert "/admin/settings" in routes
        assert "/admin/admins" in routes
