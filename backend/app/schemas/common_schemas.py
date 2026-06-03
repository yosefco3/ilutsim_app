"""Common shared schemas for API responses."""

from typing import Any

from pydantic import BaseModel


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