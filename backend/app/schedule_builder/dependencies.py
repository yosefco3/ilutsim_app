"""
Part B — schedule builder dependency providers.

FastAPI ``Depends()`` factories for the schedule-builder services live here
(NOT in ``app/dependencies.py``) to keep the part-A / part-B boundary explicit.
It is fine to import session/auth helpers from part A (dependency rule: B → A).

It is fine to import session/auth helpers from part A (dependency rule: B → A).
"""

from fastapi import Depends

from app.database import get_pool
from app.schedule_builder.repositories.attribute_repository import AttributeRepository
from app.schedule_builder.repositories.profile_repository import ProfileRepository
from app.schedule_builder.services.attribute_service import AttributeService
from app.schedule_builder.services.profile_service import ProfileService


async def get_profile_service(session=Depends(get_pool)) -> ProfileService:
    return ProfileService(ProfileRepository(session))


async def get_attribute_service(session=Depends(get_pool)) -> AttributeService:
    return AttributeService(AttributeRepository(session))
