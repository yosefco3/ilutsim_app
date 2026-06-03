"""
SettingsService — business logic for system settings management.
"""

import logging
from typing import Any, Optional

from app.exceptions import ValidationException
from app.messages import Messages
from app.models.system_settings import SystemSettings
from app.repositories.system_settings_repository import SystemSettingsRepository
from app.schemas.common_schemas import SettingsResponse

logger = logging.getLogger("ilutzim")

# Default settings keys and their types
SETTINGS_DEFAULTS: dict[str, Any] = {
    "submission_deadline_hour": 20,
    "submission_deadline_minute": 0,
    "min_guard_coverage": 2,
    "auto_absence_enabled": True,
    "telegram_bot_token": "",
    "notifications_enabled": True,
}


class SettingsService:
    """Orchestrates system-wide settings CRUD."""

    def __init__(self, settings_repo: SystemSettingsRepository) -> None:
        self._settings_repo = settings_repo

    async def get_all_settings(self) -> SettingsResponse:
        """Return all settings as a flat dict."""
        rows = await self._settings_repo.get_all()
        settings_map = {row.key: row.value for row in rows}
        # Fill defaults for missing keys
        for key, default in SETTINGS_DEFAULTS.items():
            if key not in settings_map:
                settings_map[key] = default
        return SettingsResponse(settings=settings_map)

    async def update_setting(self, key: str, value: Any) -> dict[str, Any]:
        """Update or create a single setting."""
        if key not in SETTINGS_DEFAULTS:
            raise ValidationException(f"Unknown setting: {key}")
        await self._settings_repo.upsert(key, value)
        logger.info(f"Setting updated: {key}={value}")
        return {"key": key, "value": value}

    async def get_setting(self, key: str) -> Any:
        """Get a single setting value."""
        row = await self._settings_repo.get_by_key(key)
        if row is not None:
            return row.value
        return SETTINGS_DEFAULTS.get(key)

    async def ensure_defaults(self) -> None:
        """Seed any missing default settings on startup."""
        for key, default in SETTINGS_DEFAULTS.items():
            existing = await self._settings_repo.get_by_key(key)
            if existing is None:
                await self._settings_repo.upsert(key, default)
                logger.info(f"Default setting seeded: {key}={default}")