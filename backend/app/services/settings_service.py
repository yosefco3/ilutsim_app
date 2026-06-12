"""
SettingsService — business logic for system settings management.
"""

import logging
from typing import Any

from app.exceptions import ValidationException
from app.repositories.system_settings_repository import SystemSettingsRepository
from app.schemas.common_schemas import SettingItem, SettingsUpdateRequest

logger = logging.getLogger("ilutzim")

# Default settings keys and their types
SETTINGS_DEFAULTS: dict[str, Any] = {
    "telegram_bot_token": "",
    "notifications_enabled": True,
    "shift_default_morning": "07:00-16:30",
    "shift_default_afternoon": "15:00-23:00",
    "shift_default_night": "23:00-07:00",
    # Constraint-rule thresholds — surfaced to the guard form as soft warnings.
    "min_shifts_per_guard": 5,
    "min_nights": 2,
    "min_evenings": 2,
    "max_consecutive_days": 6,
    # Week auto open/lock — placeholder config only (no scheduler wired yet).
    "auto_open_enabled": False,
    "auto_open_weekday": "thursday",
    "auto_open_time": "08:00",
    "auto_lock_enabled": False,
    "auto_lock_weekday": "saturday",
    "auto_lock_time": "20:00",
}


class SettingsService:
    """Orchestrates system-wide settings CRUD."""

    def __init__(self, settings_repo: SystemSettingsRepository) -> None:
        self._settings_repo = settings_repo

    @staticmethod
    def _to_str(value: Any) -> str:
        """Serialize a setting value to the string form stored/returned by the API."""
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    async def get_settings(self) -> list[SettingItem]:
        """Return every known setting as {key, value, description}.

        DB rows override the defaults; missing keys fall back to SETTINGS_DEFAULTS.
        Order follows SETTINGS_DEFAULTS so the admin page is stable.
        """
        rows = await self._settings_repo.get_all_settings()
        overrides = {row.setting_key: row for row in rows}
        items: list[SettingItem] = []
        for key, default in SETTINGS_DEFAULTS.items():
            row = overrides.get(key)
            if row is not None:
                items.append(
                    SettingItem(key=key, value=row.setting_value, description=row.description)
                )
            else:
                items.append(SettingItem(key=key, value=self._to_str(default)))
        return items

    async def update_settings(self, req: SettingsUpdateRequest) -> list[SettingItem]:
        """Apply a partial {key: value} update and return the full settings list."""
        for key, value in req.settings.items():
            if key not in SETTINGS_DEFAULTS:
                raise ValidationException(f"Unknown setting: {key}")
            await self._settings_repo.set(key, str(value))
            logger.info("Setting updated: %s", key)
        return await self.get_settings()

    async def get_setting(self, key: str) -> Any:
        """Get a single setting value (DB value, else the default)."""
        value = await self._settings_repo.get(key)
        if value is not None:
            return value
        return SETTINGS_DEFAULTS.get(key)

    async def get_effective_bot_token(self) -> str:
        """Active Telegram bot token: the DB value if set, else env fallback.

        Lets the admin change the token live (auth paths read this per-request).
        """
        db_val = await self._settings_repo.get("telegram_bot_token")
        if db_val:
            return str(db_val)
        from app.config import get_settings
        return get_settings().TELEGRAM_BOT_TOKEN or ""

    async def ensure_defaults(self) -> None:
        """Seed any missing default settings on startup."""
        for key, default in SETTINGS_DEFAULTS.items():
            existing = await self._settings_repo.get(key)
            if existing is None:
                await self._settings_repo.set(key, self._to_str(default))
                logger.info(f"Default setting seeded: {key}={default}")