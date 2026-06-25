"""
PositionService — business logic for positions (part B).

CRUD scoped to a profile. The positions screen is "within a selected profile",
so list/create operate by ``profile_id``; update/delete operate by position id.
Request-path methods only flush (the ``get_pool`` request dependency commits).
"""

import logging
import uuid

from app.exceptions import PositionNotFoundException
from app.schedule_builder.models.position import Position
from app.schedule_builder.repositories.position_repository import PositionRepository

logger = logging.getLogger("ilutzim")


class PositionService:
    """Orchestrates position lifecycle within a profile."""

    def __init__(self, position_repo: PositionRepository) -> None:
        self._repo = position_repo

    async def list_positions(self, profile_id: uuid.UUID) -> list[Position]:
        """Return a profile's positions, ordered for display."""
        return await self._repo.get_by_profile(profile_id)

    async def get_position(self, position_id: uuid.UUID) -> Position:
        """Return a single position or raise PositionNotFoundException."""
        return await self._get_or_raise(position_id)

    async def create_position(
        self,
        profile_id: uuid.UUID,
        name: str,
        day_schedules: dict | None = None,
        required_attributes: list | None = None,
    ) -> Position:
        """Create a position. display_order is appended within the profile."""
        order = await self._repo.max_display_order_in_profile(profile_id) + 1
        position = Position(
            profile_id=profile_id,
            name=name,
            day_schedules=day_schedules or {},
            required_attributes=required_attributes or [],
            display_order=order,
        )
        created = await self._repo.save(position)
        logger.info("Created position %s (profile=%s)", created.id, profile_id)
        return created

    async def update_position(
        self,
        position_id: uuid.UUID,
        name: str | None = None,
        day_schedules: dict | None = None,
        required_attributes: list | None = None,
    ) -> Position:
        """Update a position. Only provided (non-None) fields change."""
        await self._get_or_raise(position_id)
        fields: dict = {}
        if name is not None:
            fields["name"] = name
        if day_schedules is not None:
            fields["day_schedules"] = day_schedules
        if required_attributes is not None:
            fields["required_attributes"] = required_attributes
        if not fields:
            return await self._get_or_raise(position_id)
        updated = await self._repo.update(position_id, **fields)
        logger.info("Updated position %s", position_id)
        return updated

    async def delete_position(self, position_id: uuid.UUID) -> None:
        """Delete a position. (A profile may be left with no positions.)"""
        await self._get_or_raise(position_id)
        await self._repo.delete(position_id)
        logger.info("Deleted position %s", position_id)

    async def _get_or_raise(self, position_id: uuid.UUID) -> Position:
        position = await self._repo.get_by_id(position_id)
        if position is None:
            raise PositionNotFoundException()
        return position
