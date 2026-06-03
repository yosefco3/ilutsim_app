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
from app.controllers import (
    auth_router,
    submission_router,
    admin_users_router,
    admin_weeks_router,
    admin_events_router,
    admin_notifications_router,
    admin_export_router,
    admin_settings_router,
    admin_admins_router,
)
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

    # Start Telegram bot (only if token is configured)
    bot_started = False
    if settings.TELEGRAM_BOT_TOKEN:
        try:
            from app.bot import start_bot, setup_cron_jobs, scheduler
            await start_bot()
            setup_cron_jobs()
            scheduler.start()
            bot_started = True
            logger.info("Telegram bot and cron jobs started")
        except Exception as exc:
            logger.warning("Failed to start Telegram bot: %s", exc)
    else:
        logger.info("TELEGRAM_BOT_TOKEN not set – bot disabled")

    yield

    # Shutdown
    if bot_started:
        try:
            from app.bot import stop_bot, scheduler
            scheduler.shutdown(wait=False)
            await stop_bot()
        except Exception as exc:
            logger.warning("Error stopping bot: %s", exc)

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

    # Register routers
    app.include_router(auth_router)
    app.include_router(submission_router)
    app.include_router(admin_users_router)
    app.include_router(admin_weeks_router)
    app.include_router(admin_events_router)
    app.include_router(admin_notifications_router)
    app.include_router(admin_export_router)
    app.include_router(admin_settings_router)
    app.include_router(admin_admins_router)

    # Health check endpoint
    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()