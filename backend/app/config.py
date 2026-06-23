"""
Application configuration management using Pydantic BaseSettings.
All values are read from .env file — zero hard coding.
"""

import logging
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str
    DATABASE_URL_SYNC: str | None = None

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

    # Brute-force protection on admin login (per-process, in-memory).
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_ATTEMPT_WINDOW_MINUTES: int = 15
    LOGIN_LOCKOUT_MINUTES: int = 15

    # Logging
    LOG_LEVEL: str = "INFO"

    # Environment
    ENVIRONMENT: str = "dev"

    # Feature flags
    # Part B (schedule builder + constraints import). When False the related
    # routers are NOT registered (endpoints return 404) and the part-B default
    # seed is skipped. Production hides this half of the app via this flag.
    SCHEDULE_BUILDER_ENABLED: bool = True

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


# ── Production secret validation ──────────────────────────────────────────────
JWT_SECRET_MIN_LENGTH = 32

# Known placeholder / demo secret values that must never reach production.
WEAK_JWT_SECRETS = {
    "changeme",
    "secret",
    "your-jwt-secret-key-change-in-production",
}


def production_secret_issues(settings: "Settings") -> list[str]:
    """Return a list of secret-hardening problems (empty list means OK).

    Pure function — does not raise or log. Checks the JWT secret strength and
    the seeded admin password strength. Used by ``validate_production_secrets``.
    """
    from app.services.auth_service import password_strength_errors

    issues: list[str] = []
    secret = settings.JWT_SECRET_KEY or ""
    if len(secret) < JWT_SECRET_MIN_LENGTH:
        issues.append(
            f"JWT_SECRET_KEY קצר מדי (פחות מ-{JWT_SECRET_MIN_LENGTH} תווים)"
        )
    if secret in WEAK_JWT_SECRETS:
        issues.append("JWT_SECRET_KEY הוא ערך-דמו ידוע — יש להחליפו בערך אקראי חזק")

    pw_errors = password_strength_errors(settings.SEED_ADMIN_PASSWORD)
    if pw_errors:
        issues.append("SEED_ADMIN_PASSWORD חלשה: " + "; ".join(pw_errors))

    return issues


def validate_production_secrets(
    settings: "Settings", logger: logging.Logger | None = None
) -> None:
    """Fail-fast on weak secrets in production; warn (log) otherwise.

    In ``production`` any issue raises ``RuntimeError`` to abort startup. In
    ``dev``/``staging`` issues are logged as a warning so local work is not
    blocked.
    """
    issues = production_secret_issues(settings)
    if not issues:
        return

    log = logger or logging.getLogger("ilutzim")
    summary = "בעיות אבטחה בהגדרות הסביבה: " + " | ".join(issues)
    if settings.ENVIRONMENT == "production":
        raise RuntimeError(
            summary
            + " — קבע ערכים חזקים ב-env של השרת לפני העלייה (ראה .env.example)."
        )
    log.warning("%s (יחסם בעליית production)", summary)


settings = get_settings()
