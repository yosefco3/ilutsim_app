"""
AuthController — Telegram WebApp login and admin panel login.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_auth_service, get_current_admin, get_settings_service
from app.schemas.user_schemas import LoginRequest
from app.services.auth_service import AuthService
from app.services.settings_service import SettingsService
from app.utils.telegram_auth import get_telegram_user_id

logger = logging.getLogger("ilutzim")

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/telegram")
async def telegram_login(
    body: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
    settings_service: SettingsService = Depends(get_settings_service),
):
    """
    Authenticate a user via Telegram WebApp init_data.

    Validates the init_data, finds/creates the user, returns JWT.
    """
    if not body.init_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="init_data is required",
        )

    bot_token = await settings_service.get_effective_bot_token()
    if not bot_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bot token not configured",
        )

    telegram_id = get_telegram_user_id(body.init_data, bot_token)
    if telegram_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram data",
        )

    try:
        result = await auth_service.login_with_telegram(telegram_id)
        return result
    except Exception as e:
        logger.error(f"Telegram login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )


@router.post("/admin/login")
async def admin_login(
    body: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Authenticate an admin via username/password.

    Returns JWT with admin claims if credentials are valid.
    """
    if not body.username or not body.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required",
        )

    try:
        result = await auth_service.login_admin(body.username, body.password)
        return result
    except Exception as e:
        logger.error(f"Admin login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )


@router.get("/me")
async def get_me(admin: dict = Depends(get_current_admin)):
    """Return current admin info from JWT."""
    return {
        "id": admin.get("sub"),
        "username": admin.get("username"),
        "role": admin.get("role"),
    }