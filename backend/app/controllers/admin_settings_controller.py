"""
AdminSettingsController — admin endpoints for system settings.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.dependencies import get_settings_service, require_admin_role
from app.schemas.common_schemas import SettingItem, SettingsUpdateRequest
from app.services.settings_service import SettingsService


class TelegramTokenApply(BaseModel):
    """Body for applying a new Telegram bot token live."""
    token: str

logger = logging.getLogger("ilutzim")

router = APIRouter(
    prefix="/admin/settings",
    tags=["Admin – Settings"],
    dependencies=[Depends(require_admin_role)],
)


@router.get("", response_model=list[SettingItem])
async def get_settings(
    settings_service: SettingsService = Depends(get_settings_service),
):
    """Get all system settings as [{key, value, description}]."""
    return await settings_service.get_settings()


@router.put("", response_model=list[SettingItem])
async def update_settings(
    data: SettingsUpdateRequest,
    settings_service: SettingsService = Depends(get_settings_service),
):
    """Apply a partial {settings: {key: value}} update; returns the full list."""
    try:
        return await settings_service.update_settings(data)
    except Exception as e:
        logger.error(f"Settings update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/telegram/apply")
async def apply_telegram_token(
    body: TelegramTokenApply,
    settings_service: SettingsService = Depends(get_settings_service),
):
    """Validate a new Telegram bot token, persist it, and restart the bot live.

    Validation (getMe) happens BEFORE touching the running bot, so an invalid
    token returns 400 and leaves the current bot untouched.
    """
    token = body.token.strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="טוקן ריק")

    # 1) Validate against Telegram without disturbing the running bot.
    from aiogram import Bot

    probe = Bot(token=token)
    try:
        me = await probe.get_me()
    except Exception as e:
        logger.warning("Telegram token validation failed: %s", type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"טוקן לא תקין: {e}",
        )
    finally:
        await probe.session.close()

    # 2) Persist to DB (source of truth) and 3) restart the live bot.
    await settings_service.update_settings(
        SettingsUpdateRequest(settings={"telegram_bot_token": token})
    )
    from app.bot import restart_bot_with_token

    await restart_bot_with_token(token)
    logger.info("Telegram bot token applied; bot @%s", me.username)
    return {"ok": True, "bot_username": me.username}