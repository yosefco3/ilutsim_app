"""Tests for submission success notification and detailed submissions endpoint."""
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.user import User
from app.models.schedule_week import ScheduleWeek
from app.models.weekly_submission import WeeklySubmission
from app.schemas.submission_schemas import SubmissionCreate, DayStatusInput, ShiftWindowInput
from app.services.submission_service import SubmissionService


class TestSubmissionSuccessNotification:
    """Test that successful submission triggers Telegram notification."""

    @pytest.mark.asyncio
    async def test_submit_schedule_sends_notification(self, client, db_session, test_user, open_week):
        """POST /submissions should send a Telegram notification on success."""
        payload = {
            "week_id": str(open_week.id),
            "general_notes": "test notes",
            "days": [
                {
                    "day_index": 0,
                    "shifts": [
                        {"shift_type": "morning", "from_hour": "07:00", "to_hour": "16:00"},
                    ],
                },
                {
                    "day_index": 1,
                    "shifts": [
                        {"shift_type": "night", "from_hour": "23:00", "to_hour": "07:00"},
                    ],
                },
            ],
        }

        with patch("app.controllers.submission_controller.notify_submission_success", new_callable=AsyncMock) as mock_notify:
            mock_notify.return_value = True

            response = client.post(
                "/api/submissions",
                json=payload,
                headers={"X-Telegram-Init-Data": "test-init-data"},
            )
            assert response.status_code == 201
            # Notification should have been called
            mock_notify.assert_called_once()
            args = mock_notify.call_args[0]
            # First arg should be telegram_id (int)
            assert isinstance(args[0], int)
            # Second arg should be week label string
            assert isinstance(args[1], str)
            assert "/" in args[1]  # date format DD/MM/YYYY - DD/MM/YYYY


class TestNotificationsNonCritical:
    """Notification failure should not affect the submission API response."""

    @pytest.mark.asyncio
    async def test_submit_does_not_fail_when_notification_errors(self, client, db_session, test_user, open_week):
        """Submission should succeed even if notification fails."""
        payload = {
            "week_id": str(open_week.id),
            "general_notes": "",
            "days": [
                {
                    "day_index": 0,
                    "shifts": [
                        {"shift_type": "morning", "from_hour": "08:00", "to_hour": "16:00"},
                    ],
                },
            ],
        }

        with patch("app.controllers.submission_controller.notify_submission_success", side_effect=Exception("Boom")):
            response = client.post(
                "/api/submissions",
                json=payload,
                headers={"X-Telegram-Init-Data": "test-init-data"},
            )
            # Should still return 201 despite notification failure
            assert response.status_code == 201
            data = response.json()
            assert data["general_notes"] == ""


class TestDetailedSubmissions:
    """Test the detailed submissions endpoint."""

    @pytest.mark.asyncio
    async def test_detailed_submissions_returns_submitted_and_missing(self, client, db_session, admin_headers, test_user, open_week):
        """GET /admin/weeks/{id}/submissions/detailed returns grouped data."""
        # Create a submission for test_user
        from app.models.weekly_submission import WeeklySubmission
        from app.models.daily_status import DailyStatus
        from app.models.shift_window import ShiftWindow
        from datetime import date, time

        sub = WeeklySubmission(
            user_id=test_user.id,
            week_id=open_week.id,
            general_notes="submitted notes",
        )
        db_session.add(sub)
        db_session.flush()

        day = DailyStatus(
            submission_id=sub.id,
            date=open_week.start_date,
            is_available=True,
        )
        db_session.add(day)
        db_session.flush()

        shift = ShiftWindow(
            daily_status_id=day.id,
            shift_type="morning",
            start_time=time(7, 0),
            end_time=time(16, 0),
        )
        db_session.add(shift)
        db_session.commit()

        response = client.get(
            f"/api/admin/weeks/{open_week.id}/submissions/detailed",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "submitted" in data
        assert "missing" in data
        assert "week_label" in data

        # test_user should be in submitted
        assert len(data["submitted"]) >= 1
        submitted_ids = [s["user_id"] for s in data["submitted"]]
        assert str(test_user.id) in submitted_ids

        # Check shift data is present
        for s in data["submitted"]:
            if s["user_id"] == str(test_user.id):
                assert len(s["days"]) >= 1
                assert s["general_notes"] == "submitted notes"
                assert s["full_name"] == f"{test_user.first_name} {test_user.last_name}"