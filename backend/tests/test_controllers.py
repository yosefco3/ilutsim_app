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
from app.controllers.admin_notifications_controller import router as admin_notif_router
from app.controllers.admin_export_controller import router as admin_export_router
from app.controllers.admin_settings_controller import router as admin_settings_router
from app.controllers.admin_admins_controller import router as admin_admins_router
from app.dependencies import (
    get_auth_service,
    get_current_admin,
    get_settings_service,
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
        mock_svc.login_with_telegram.return_value = {"token": "jwt-token-abc"}

        mock_settings = AsyncMock()
        mock_settings.get_effective_bot_token.return_value = "test-token"

        app = _make_app()
        app.dependency_overrides[get_auth_service] = lambda: mock_svc
        app.dependency_overrides[get_settings_service] = lambda: mock_settings
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
        """GET /submissions/current-week returns 200 + null when no active week."""
        mock_svc = AsyncMock()
        mock_svc.get_relevant_week_with_days.return_value = None

        app = _make_app()
        app.dependency_overrides[get_week_service] = lambda: mock_svc
        client = TestClient(app)

        resp = client.get("/submissions/current-week")
        assert resp.status_code == 200
        assert resp.json() is None
        app.dependency_overrides.clear()

    def test_get_current_week_success(self):
        """GET /submissions/current-week returns data when available."""
        from datetime import date

        mock_svc = AsyncMock()
        mock_svc.get_relevant_week_with_days.return_value = {
            "id": str(uuid.uuid4()),
            "start_date": date(2025, 1, 6),
            "end_date": date(2025, 1, 12),
            "status": "open",
            "days": [{"day_index": i, "blocked": False} for i in range(7)],
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

    # ── new-guard open-week notification ─────────────────────────────────

    def _user_obj(self, telegram_id="555"):
        from datetime import datetime, timezone
        return type("U", (), {
            "id": uuid.uuid4(),
            "phone_number": "0500000000",
            "first_name": "דנה",
            "last_name": "כהן",
            "full_name": "דנה כהן",
            "role": "BASIC_GUARD",
            "is_active": True,
            "telegram_id": telegram_id,
            "exemptions_notes": None,
            "min_total_shifts": 0,
            "min_night_shifts": 0,
            "min_evening_shifts": 0,
            "created_at": datetime.now(timezone.utc),
        })()

    def _open_week(self):
        from datetime import date
        return type("W", (), {
            "start_date": date(2026, 6, 8),
            "end_date": date(2026, 6, 14),
        })()

    def _post_payload(self):
        return {
            "phone_number": "0500000000",
            "first_name": "דנה",
            "last_name": "כהן",
            "role": "BASIC_GUARD",
        }

    @patch("app.bot.notifications.notify_week_opened", new_callable=AsyncMock)
    def test_create_user_notifies_when_week_open(self, mock_notify):
        user_svc = AsyncMock()
        user_svc.create_user.return_value = self._user_obj(telegram_id="555")
        week_svc = AsyncMock()
        week_svc.get_current_open_week.return_value = self._open_week()

        app = _make_app()
        app.dependency_overrides[require_admin_role] = _mock_admin_payload
        app.dependency_overrides[get_user_service] = lambda: user_svc
        app.dependency_overrides[get_week_service] = lambda: week_svc
        client = TestClient(app)

        resp = client.post("/admin/users", json=self._post_payload())
        assert resp.status_code == 201
        mock_notify.assert_awaited_once()
        # called with the new guard's telegram_id in the recipients list
        assert mock_notify.await_args.args[2] == [555]
        app.dependency_overrides.clear()

    @patch("app.bot.notifications.notify_week_opened", new_callable=AsyncMock)
    def test_create_user_no_notice_when_no_open_week(self, mock_notify):
        user_svc = AsyncMock()
        user_svc.create_user.return_value = self._user_obj(telegram_id="555")
        week_svc = AsyncMock()
        week_svc.get_current_open_week.return_value = None

        app = _make_app()
        app.dependency_overrides[require_admin_role] = _mock_admin_payload
        app.dependency_overrides[get_user_service] = lambda: user_svc
        app.dependency_overrides[get_week_service] = lambda: week_svc
        client = TestClient(app)

        resp = client.post("/admin/users", json=self._post_payload())
        assert resp.status_code == 201
        mock_notify.assert_not_awaited()
        app.dependency_overrides.clear()

    @patch("app.bot.notifications.notify_week_opened", new_callable=AsyncMock)
    def test_create_user_no_notice_without_telegram_id(self, mock_notify):
        user_svc = AsyncMock()
        user_svc.create_user.return_value = self._user_obj(telegram_id=None)
        week_svc = AsyncMock()
        week_svc.get_current_open_week.return_value = self._open_week()

        app = _make_app()
        app.dependency_overrides[require_admin_role] = _mock_admin_payload
        app.dependency_overrides[get_user_service] = lambda: user_svc
        app.dependency_overrides[get_week_service] = lambda: week_svc
        client = TestClient(app)

        resp = client.post("/admin/users", json=self._post_payload())
        assert resp.status_code == 201
        mock_notify.assert_not_awaited()
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

    @patch("app.bot.notifications.notify_closing_reminder", new_callable=AsyncMock)
    def test_remind_sends_only_to_non_submitters(self, mock_notify):
        from datetime import date
        from types import SimpleNamespace

        week_id = uuid.uuid4()
        submitted = SimpleNamespace(id=uuid.uuid4(), telegram_id="111")
        missing = SimpleNamespace(id=uuid.uuid4(), telegram_id="222")
        no_telegram = SimpleNamespace(id=uuid.uuid4(), telegram_id=None)

        week_svc = AsyncMock()
        week_svc.get_week.return_value = SimpleNamespace(
            id=week_id, start_date=date(2025, 6, 14)
        )
        user_svc = AsyncMock()
        user_svc.get_all_active_users.return_value = [submitted, missing, no_telegram]
        sub_svc = AsyncMock()
        # Only `submitted` has a submission; the others haven't submitted.
        sub_svc.get_submission.side_effect = lambda uid, wid: (
            object() if uid == submitted.id else None
        )

        app = _make_app()
        app.dependency_overrides[require_admin_role] = _mock_admin_payload
        app.dependency_overrides[get_week_service] = lambda: week_svc
        app.dependency_overrides[get_user_service] = lambda: user_svc
        app.dependency_overrides[get_submission_service] = lambda: sub_svc
        client = TestClient(app)

        resp = client.post(f"/admin/notifications/remind/{week_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["reminded"] == 1
        assert body["total_active"] == 3
        mock_notify.assert_awaited_once()
        # Only the missing guard WITH a telegram_id is reminded (as an int).
        assert mock_notify.await_args.kwargs["telegram_ids"] == [222]
        app.dependency_overrides.clear()


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
