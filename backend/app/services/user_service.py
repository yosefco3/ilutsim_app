"""
UserService — business logic for user (guard) management.
"""

import logging
import uuid

from app.exceptions import UserDeactivatedException, UserNotFoundException
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schemas import UserCreate, UserResponse, UserUpdate

logger = logging.getLogger("ilutzim")


class UserService:
    """Orchestrates user CRUD with business rules."""

    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def create_user(self, data: UserCreate) -> UserResponse:
        """Create a new guard and return the response."""
        logger.info(f"Creating user with phone={data.phone_number}")
        user = User(
            phone_number=data.phone_number,
            full_name=data.full_name,
            role=data.role,
            min_total_shifts=data.min_total_shifts,
            min_night_shifts=data.min_night_shifts,
            min_evening_shifts=data.min_evening_shifts,
            exemptions_notes=data.exemptions_notes,
        )
        created = await self._user_repo.save(user)
        logger.info(f"User created: id={created.id}")
        return UserResponse.model_validate(created)

    async def update_user(self, user_id: uuid.UUID, data: UserUpdate) -> UserResponse:
        """Update an existing guard's details."""
        user = await self._get_user_or_raise(user_id)
        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        updated = await self._user_repo.save(user)
        logger.info(f"User updated: id={user_id}")
        return UserResponse.model_validate(updated)

    async def deactivate_user(self, user_id: uuid.UUID) -> UserResponse:
        """Set is_active=False for a guard."""
        user = await self._get_user_or_raise(user_id)
        user.is_active = False
        updated = await self._user_repo.save(user)
        logger.info(f"User deactivated: id={user_id}")
        return UserResponse.model_validate(updated)

    async def get_all_active_users(self) -> list[UserResponse]:
        """Return only active guards."""
        users = await self._user_repo.get_active_users()
        return [UserResponse.model_validate(u) for u in users]

    async def get_user(self, user_id: uuid.UUID) -> UserResponse:
        """Get a single guard by ID."""
        user = await self._get_user_or_raise(user_id)
        return UserResponse.model_validate(user)

    async def link_telegram(self, phone_number: str, telegram_id: str) -> UserResponse:
        """Bot authentication: find user by phone and link telegram_id."""
        user = await self._user_repo.get_by_phone(phone_number)
        if user is None:
            logger.warning(f"Telegram link failed — phone not found: {phone_number}")
            raise UserNotFoundException()
        user = await self._user_repo.link_telegram_id(user.id, telegram_id)
        logger.info(f"Telegram linked: user_id={user.id}, telegram_id={telegram_id}")
        return UserResponse.model_validate(user)

    # ── Internal helpers ──────────────────────────────────────────────────

    async def _get_user_or_raise(self, user_id: uuid.UUID) -> User:
        """Fetch user or raise UserNotFoundException."""
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundException()
        return user