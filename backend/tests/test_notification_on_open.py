"""Tests for week-opened Telegram notification (P06)."""

import asyncio
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.bot.notifications import notify_week_opened


# ---------------------------------------------------------------------------
# Helper to build a mock user object
# ---------------------------------------------------------------------------
def _make_user(telegram_id=None):
    u = MagicMock()
    u.telegram_id = telegram_id
    return u


# ===========================================================================
# Test: notify_week_opened sends to all guards with telegram_id
# ===========================================================================
@pytest.mark.asyncio
async def test_notify_week_opened_sends_to_all_guards():
    """Should call send_message for every user with a telegram_id."""
    ids = [111, 222, 333]
    with patch("app.bot.notifications.get_bot") as mock_bot_fn:
        mock_bot = AsyncMock()
        mock_bot_fn.return_value = mock_bot

        count = await notify_week_opened(date(2026, 6, 8), date(2026, 6, 14), ids)

    assert count == 3
    assert mock_bot.send_message.call_count == 3


# ===========================================================================
# Test: skips users without telegram_id (empty list)
# ===========================================================================
@pytest.mark.asyncio
async def test_notify_week_opened_handles_empty_list():
    """Should return 0 when no telegram_ids provided."""
    with patch("app.bot.notifications.get_bot") as mock_bot_fn:
        mock_bot = AsyncMock()
        mock_bot_fn.return_value = mock_bot

        count = await notify_week_opened(date(2026, 6, 8), date(2026, 6, 14), [])

    assert count == 0
    assert mock_bot.send_message.call_count == 0


# ===========================================================================
# Test: one failure doesn't stop others
# ===========================================================================
@pytest.mark.asyncio
async def test_notify_week_opened_continues_on_error():
    """If sending to one user fails, others should still be notified."""
    ids = [111, 222, 333]

    with patch("app.bot.notifications.get_bot") as mock_bot_fn:
        mock_bot = AsyncMock()
        mock_bot_fn.return_value = mock_bot

        # Second call raises
        mock_bot.send_message.side_effect = [
            None,                       # success (returns coro result None)
            Exception("boom"),          # failure
            None,                       # success
        ]

        count = await notify_week_opened(date(2026, 6, 8), date(2026, 6, 14), ids)

    # Two succeeded, one failed
    assert count == 2
    assert mock_bot.send_message.call_count == 3


# ===========================================================================
# Test: notification message format (DD/MM/YYYY + webapp URL)
# ===========================================================================
@pytest.mark.asyncio
async def test_notification_message_format():
    """Message must use DD/MM/YYYY format and include WEBAPP_URL."""
    captured_texts: list[str] = []

    with patch("app.bot.notifications.get_bot") as mock_bot_fn, \
         patch("app.config.settings") as mock_settings:
        mock_bot = AsyncMock()
        mock_bot_fn.return_value = mock_bot
        mock_settings.WEBAPP_URL = "https://example.com/app"

        def capture_send(*, chat_id, text):
            captured_texts.append(text)
            return asyncio.get_event_loop().create_future().set_result(None) or None

        # Make send_message capture the text
        async def fake_send(**kwargs):
            captured_texts.append(kwargs["text"])

        mock_bot.send_message = AsyncMock(side_effect=fake_send)

        await notify_week_opened(date(2026, 6, 8), date(2026, 6, 14), [111])

    assert len(captured_texts) == 1
    msg = captured_texts[0]
    assert "08/06/2026" in msg
    assert "14/06/2026" in msg
    assert "https://example.com/app" in msg
    assert "שבוע חדש נפתח להגשה" in msg