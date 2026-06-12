"""Tests for live Telegram bot-token apply.

POST /admin/settings/telegram/apply validates the token via getMe BEFORE
touching the running bot, persists it, then hot-restarts the bot. An invalid
token must leave the running bot (and the stored value) untouched.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.controllers.admin_settings_controller import router
from app.dependencies import get_settings_service, require_admin_role
from app.services.settings_service import SettingsService


def _make_app(svc):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_settings_service] = lambda: svc
    app.dependency_overrides[require_admin_role] = lambda: {"role": "admin"}
    return app


def _fake_bot(username="my_bot", get_me_error=None):
    bot = MagicMock()
    bot.session.close = AsyncMock()
    if get_me_error is not None:
        bot.get_me = AsyncMock(side_effect=get_me_error)
    else:
        bot.get_me = AsyncMock(return_value=MagicMock(username=username))
    return bot


def test_valid_token_persists_and_restarts():
    svc = AsyncMock()
    client = TestClient(_make_app(svc))

    with patch("aiogram.Bot", return_value=_fake_bot("safra_bot")), \
         patch("app.bot.restart_bot_with_token", new=AsyncMock()) as restart:
        resp = client.post("/admin/settings/telegram/apply", json={"token": "123:abc"})

    assert resp.status_code == 200
    assert resp.json() == {"ok": True, "bot_username": "safra_bot"}
    svc.update_settings.assert_awaited_once()
    restart.assert_awaited_once_with("123:abc")


def test_invalid_token_leaves_running_bot_untouched():
    svc = AsyncMock()
    client = TestClient(_make_app(svc))

    with patch("aiogram.Bot", return_value=_fake_bot(get_me_error=Exception("Unauthorized"))), \
         patch("app.bot.restart_bot_with_token", new=AsyncMock()) as restart:
        resp = client.post("/admin/settings/telegram/apply", json={"token": "bad"})

    assert resp.status_code == 400
    svc.update_settings.assert_not_awaited()
    restart.assert_not_awaited()


def test_empty_token_rejected():
    svc = AsyncMock()
    client = TestClient(_make_app(svc))
    resp = client.post("/admin/settings/telegram/apply", json={"token": "  "})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_effective_token_prefers_db():
    repo = AsyncMock()
    repo.get.return_value = "db-token"
    assert await SettingsService(repo).get_effective_bot_token() == "db-token"


@pytest.mark.asyncio
async def test_effective_token_falls_back_to_env(monkeypatch):
    repo = AsyncMock()
    repo.get.return_value = None
    import app.config

    monkeypatch.setattr(
        app.config, "get_settings", lambda: MagicMock(TELEGRAM_BOT_TOKEN="env-token")
    )
    assert await SettingsService(repo).get_effective_bot_token() == "env-token"
