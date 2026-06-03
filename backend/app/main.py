"""
FastAPI application factory with lifespan, CORS, exception handlers, and health check.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.exceptions import (
    AppBaseException,
    app_exception_handler,
    generic_exception_handler,
    validation_exception_handler,
)
from app.logging_config import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle."""
    settings = get_settings()
    setup_logging(settings.LOG_LEVEL, settings.ENVIRONMENT)
    logger = logging.getLogger("ilutzim")
    logger.info("Application starting", extra={"extra_data": {"environment": settings.ENVIRONMENT}})
    yield
    logger.info("Application shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Ilutzim App",
        description="Security Guard Shift Management System",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.WEBAPP_URL, settings.ADMIN_DASHBOARD_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Global exception handlers
    app.add_exception_handler(AppBaseException, app_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, generic_exception_handler)  # type: ignore[arg-type]

    # Health check endpoint
    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()