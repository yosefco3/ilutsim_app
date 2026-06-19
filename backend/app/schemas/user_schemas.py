"""User schemas with Israeli phone validation."""

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants import UserRole
from app.messages import Messages


def _validate_israeli_phone(phone: str) -> str:
    """Validate and normalize Israeli phone number to 972XXXXXXXXX format.

    Accepts formats:
    - 05XXXXXXXX (10 digits starting with 05)
    - +972XXXXXXXXX (+972 followed by 9 digits)
    - 972XXXXXXXXX (972 followed by 9 digits)
    - With spaces/dashes that get stripped

    Always returns in 972XXXXXXXXX format (no leading +).
    """
    # Strip spaces, dashes, and leading +
    cleaned = phone.replace(" ", "").replace("-", "")
    if cleaned.startswith("+"):
        cleaned = cleaned[1:]

    # Israeli local format: starts with 05, 10 digits total → normalize to 972
    if re.match(r"^05\d{8}$", cleaned):
        return "972" + cleaned[1:]

    # International format: 972 followed by 9 digits
    if re.match(r"^972\d{9}$", cleaned):
        return cleaned

    raise ValueError(Messages.VAL_INVALID_PHONE)


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    phone_number: str
    first_name: str
    last_name: str
    role: UserRole
    exemptions_notes: str | None = None
    min_total_shifts: int = 0
    min_night_shifts: int = 0
    min_evening_shifts: int = 0

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return _validate_israeli_phone(v)


class UserUpdate(BaseModel):
    """Schema for updating a user — all fields optional."""
    phone_number: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    exemptions_notes: str | None = None
    min_total_shifts: int | None = None
    min_night_shifts: int | None = None
    min_evening_shifts: int | None = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return _validate_israeli_phone(v)


class UserResponse(BaseModel):
    """Schema for user data in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    phone_number: str
    first_name: str
    last_name: str
    full_name: str | None = None
    role: UserRole
    is_active: bool
    telegram_id: str | None = None
    exemptions_notes: str | None = None
    min_total_shifts: int = 0
    min_night_shifts: int = 0
    min_evening_shifts: int = 0
    created_at: datetime


class UserListResponse(BaseModel):
    """Paginated list of users."""
    users: list[UserResponse]
    count: int


# ── Admin schemas ────────────────────────────────────────────────────────────

from app.constants import AdminRole


class AdminCreate(BaseModel):
    """Schema for creating a new admin."""
    email: str
    password: str
    full_name: str
    role: AdminRole = AdminRole.ADMIN


class AdminUpdate(BaseModel):
    """Schema for updating an admin."""
    email: str | None = None
    full_name: str | None = None
    role: AdminRole | None = None
    is_active: bool | None = None
    password: str | None = None


class AdminResponse(BaseModel):
    """Schema for admin data in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: AdminRole
    is_active: bool
    created_at: datetime


# ── Auth schemas ──────────────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    """Schema for login requests (telegram and admin)."""
    init_data: str | None = None
    username: str | None = None
    password: str | None = None


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: AdminResponse


class ChangePasswordRequest(BaseModel):
    """Schema for admin self-service password change."""
    current_password: str
    new_password: str
