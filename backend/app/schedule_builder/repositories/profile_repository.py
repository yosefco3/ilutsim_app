"""
ProfileRepository — data access for activation profiles (part B).
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base_repository import BaseRepository
from app.schedule_builder.models.activation_profile import ActivationProfile


class ProfileRepository(BaseRepository[ActivationProfile]):
    """Data-access operations for ActivationProfile entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ActivationProfile)

    async def get_all_ordered(self) -> list[ActivationProfile]:
        """Return all profiles ordered by display_order, then created_at."""
        stmt = select(self.model_class).order_by(
            ActivationProfile.display_order.asc(),
            ActivationProfile.created_at.asc(),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_default(self) -> ActivationProfile | None:
        """Return the profile flagged is_default, if any."""
        stmt = select(self.model_class).where(ActivationProfile.is_default.is_(True))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def count(self) -> int:
        """Return the total number of profiles."""
        result = await self.session.execute(select(func.count(ActivationProfile.id)))
        return result.scalar()

    async def max_display_order(self) -> int:
        """Return the highest display_order in use (0 if no profiles)."""
        result = await self.session.execute(
            select(func.coalesce(func.max(ActivationProfile.display_order), 0))
        )
        return result.scalar() or 0
