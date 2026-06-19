"""
AdminSettingsController — admin endpoints for system settings.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_settings_service, require_admin_role
from app.schemas.common_schemas import SettingItem, SettingsUpdateRequest
from app.services.settings_service import SettingsService

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
        result = await settings_service.update_settings(data)
    except Exception as e:
        logger.error(f"Settings update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # If any auto-open/lock setting changed, reschedule the cron jobs so the
    # change takes effect immediately (no restart needed).
    if any(key.startswith(("auto_open", "auto_lock")) for key in data.settings):
        try:
            from app.scheduler import sync_automation_jobs

            await sync_automation_jobs()
        except Exception as exc:
            logger.warning("Failed to reschedule automation jobs: %s", exc)

    return result