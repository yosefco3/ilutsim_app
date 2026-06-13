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

    # App (unified — serves both admin and guard interfaces)
    APP_URL: str

    # Admin
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

    # Automatic weekly rollover (Motzaei Shabbat — Sunday 00:00 Israel time):
    # auto-lock the active submission week and ensure the upcoming one.
    AUTO_ROLLOVER_ENABLED: bool = True
    SCHEDULER_TIMEZONE: str = "Asia/Jerusalem"

    # Data retention — keep only the most recent N weeks (by start_date).
    # Older weeks (including published) are auto-purged during the weekly
    # rollover so the database does not grow without bound.
    RETENTION_ENABLED: bool = True
    RETENTION_WEEKS: int = 60

    # Seed — default admin user
    SEED_ADMIN_EMAIL: str = "admin@test.com"
    SEED_ADMIN_PASSWORD: str = "admin123"
    SEED_ADMIN_FULL_NAME: str = "Test Admin"

    @property
    def cors_origins(self) -> list[str]:
        """CORS-allowed origins."""
        origins = [self.APP_URL]
        if self.ENVIRONMENT == "dev":
            origins.append("http://localhost:3001")
        return origins

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
