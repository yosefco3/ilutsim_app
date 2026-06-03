"""
AuthService — JWT token creation, password hashing, and admin authentication.
"""

import logging
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import Settings
from app.exceptions import AuthenticationFailedException
from app.models.admin import Admin
from app.repositories.admin_repository import AdminRepository

logger = logging.getLogger("ilutzim")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Handles JWT token creation and admin login verification."""

    def __init__(self, admin_repo: AdminRepository, settings: Settings) -> None:
        self._admin_repo = admin_repo
        self._settings = settings

    async def authenticate_admin(self, email: str, password: str) -> dict:
        """Verify admin credentials and return a JWT token dict."""
        admin = await self._admin_repo.get_by_email(email)
        if admin is None or not admin.is_active:
            logger.warning(f"Admin login failed — email not found or inactive: {email}")
            raise AuthenticationFailedException()

        if not pwd_context.verify(password, admin.password_hash):
            logger.warning(f"Admin login failed — bad password: {email}")
            raise AuthenticationFailedException()

        token = self._create_access_token(
            data={"sub": str(admin.id), "role": admin.role.value}
        )
        logger.info(f"Admin authenticated: {email}")
        return {
            "access_token": token,
            "token_type": "bearer",
            "admin_id": admin.id,
            "role": admin.role.value,
        }

    def verify_token(self, token: str) -> dict:
        """Decode and validate a JWT token. Returns payload dict."""
        try:
            payload = jwt.decode(
                token,
                self._settings.JWT_SECRET_KEY,
                algorithms=[self._settings.JWT_ALGORITHM],
            )
            return payload
        except JWTError as exc:
            logger.warning(f"JWT verification failed: {exc}")
            raise AuthenticationFailedException()

    def _create_access_token(self, data: dict) -> str:
        """Build a JWT with expiration."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self._settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode["exp"] = expire
        return jwt.encode(
            to_encode,
            self._settings.JWT_SECRET_KEY,
            algorithm=self._settings.JWT_ALGORITHM,
        )

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plaintext password (used for seeding / admin creation)."""
        return pwd_context.hash(password)