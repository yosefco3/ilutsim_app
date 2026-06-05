"""
Application configuration management using Pydantic BaseSettings.
All values are read from .env file — zero hard coding.
"""

from functools import lru_cache
from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str
    DATABASE_URL_SYNC: Optional[str] = None

    # Telegram
    TELEGRAM_BOT_TOKEN: str

    # Web App
    WEBAPP_URL: str

    # Admin
    ADMIN_DASHBOARD_URL: str
    ADMIN_API_KEY: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"

    # Environment
    ENVIRONMENT: str = "dev"

    # Cron / Scheduling
    CRON_WEEKLY_OPEN_DAY: str = "sunday"
    CRON_WEEKLY_OPEN_HOUR: str = "09:00"
    REMINDER_HOUR: int = 18

    @property
    def reminder_hour(self) -> int:
        """Hour for closing reminder cron (alias for REMINDER_HOUR)."""
        return self.REMINDER_HOUR

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
         "extra": "ignore",   
    }


@lru_cache
def get_settings() -> Settings:
    """Return cached Settings singleton."""
    return Settings()


settings = get_settings()
