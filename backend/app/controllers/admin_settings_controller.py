"""
AdminSettingsController — admin endpoints for system settings.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_settings_service, require_admin_role
from app.schemas.common_schemas import SettingsResponse, SettingsUpdate
from app.services.settings_service import SettingsService

logger = logging.getLogger("ilutzim")

router = APIRouter(
    prefix="/admin/settings",
    tags=["Admin – Settings"],
    dependencies=[Depends(require_admin_role)],
)


@router.get("", response_model=SettingsResponse)
async def get_settings(
    settings_service: SettingsService = Depends(get_settings_service),
):
    """Get all system settings."""
    return await settings_service.get_settings()


@router.patch("", response_model=SettingsResponse)
async def update_settings(
    data: SettingsUpdate,
    settings_service: SettingsService = Depends(get_settings_service),
):
    """Update system settings."""
    try:
        return await settings_service.update_settings(data)
    except Exception as e:
        logger.error(f"Settings update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )