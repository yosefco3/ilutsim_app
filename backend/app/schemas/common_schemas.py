"""Common shared schemas for API responses."""

from typing import Any

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApiResponse(BaseModel):
    """Generic success response wrapper."""
    success: bool
    message: str
    data: Any | None = None


class ErrorResponse(BaseModel):
    """Generic error response."""
    success: bool = False
    error: str
    detail: str | None = None


class TokenResponse(BaseModel):
    """JWT token response."""
    token: str


# ── Settings schemas ──────────────────────────────────────────────────────────


class SettingsUpdate(BaseModel):
    """Schema for updating system settings."""
    setting_value: str
    description: str | None = None


class SettingsResponse(BaseModel):
    """Schema for system setting in API responses."""
    model_config = ConfigDict(from_attributes=True)

    setting_key: str
    setting_value: str
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
