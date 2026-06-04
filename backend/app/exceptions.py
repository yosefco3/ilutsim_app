"""
Custom exception classes and global FastAPI exception handlers.
"""

import logging
import traceback

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.messages import Messages

logger = logging.getLogger("ilutzim")


# ── Base exception ────────────────────────────────────────────────────


class AppBaseException(Exception):
    """Base exception for all application-specific errors."""

    status_code: int = 500
    message: str = "שגיאה פנימית"

    def __init__(self, message: str | None = None) -> None:
        if message is not None:
            self.message = message
        super().__init__(self.message)


# ── Concrete exceptions ───────────────────────────────────────────────


class WeekLockedException(AppBaseException):
    status_code = 403
    message = Messages.ERR_WEEK_LOCKED


class UserNotAuthorizedException(AppBaseException):
    status_code = 401
    message = Messages.ERR_AUTH_FAILED


class UserDeactivatedException(AppBaseException):
    status_code = 403
    message = Messages.ERR_USER_DEACTIVATED


class UserNotFoundException(AppBaseException):
    status_code = 404
    message = Messages.ERR_USER_NOT_FOUND


class ValidationException(AppBaseException):
    status_code = 422
    message = Messages.ERR_VALIDATION


class ConflictException(AppBaseException):
    status_code = 409
    message = Messages.ERR_CONFLICT


class AdminNotFoundException(AppBaseException):
    status_code = 404
    message = Messages.ERR_USER_NOT_FOUND


class AuthenticationFailedException(AppBaseException):
    """Raised when Telegram authentication fails."""
    status_code = 401


class InvalidCredentialsException(AppBaseException):
    status_code = 401
    message = Messages.ERR_AUTH_FAILED


class TokenExpiredException(AppBaseException):
    status_code = 401
    message = Messages.ERR_AUTH_FAILED


class InsufficientPermissionsException(AppBaseException):
    status_code = 403
    message = Messages.ERR_AUTH_FAILED


# ── Global exception handlers ─────────────────────────────────────────


async def app_exception_handler(request: Request, exc: AppBaseException) -> JSONResponse:
    """Handle all AppBaseException subclasses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.message, "detail": None},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic RequestValidationError."""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": Messages.ERR_VALIDATION,
            "detail": exc.errors(),
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler — logs traceback and returns 500."""
    logger.error(f"Unhandled exception: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "שגיאה פנימית בשרת", "detail": None},
    )