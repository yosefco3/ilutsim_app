"""
Tests for PositionService (part B — schedule builder).
"""

import uuid

import pytest

from app.exceptions import PositionNotFoundException
from app.schedule_builder.models.activation_profile import ActivationProfile
from app.schedule_builder.repositories.position_repository import PositionRepository
from app.schedule_builder.services.position_service import PositionService


@pytest.fixture
def service(db_session):
    return PositionService(PositionRepository(db_session))


async def _make_profile(db_session, name="שגרה"):
    profile = ActivationProfile(name=name)
    db_session.add(profile)
    await db_session.flush()
    return profile


class TestCrud:
    async def test_create_then_list_ordered(self, service, db_session):
        profile = await _make_profile(db_session)
        await service.create_position(profile.id, "ארנונה")
        await service.create_position(profile.id, "קומה 6")
        positions = await service.list_positions(profile.id)

        assert [p.name for p in positions] == ["ארנונה", "קומה 6"]
        assert positions[0].display_order < positions[1].display_order

    async def test_display_order_is_per_profile(self, service, db_session):
        a = await _make_profile(db_session, "שגרה")
        b = await _make_profile(db_session, "חג")
        await service.create_position(a.id, "א1")
        first_b = await service.create_position(b.id, "ב1")
        # Profile b starts its own ordering at 1.
        assert first_b.display_order == 1

    async def test_create_with_payload(self, service, db_session):
        profile = await _make_profile(db_session)
        sched = {"0": {"start": "07:30", "end": "15:00"}}
        pos = await service.create_position(
            profile.id, "ארנונה",
            day_schedules=sched, required_attributes=["armed"],
        )
        assert pos.day_schedules == sched
        assert pos.required_attributes == ["armed"]

    async def test_update_only_provided_fields(self, service, db_session):
        profile = await _make_profile(db_session)
        pos = await service.create_position(
            profile.id, "ארנונה",
            day_schedules={"0": {"start": "07:00", "end": "15:00"}},
            required_attributes=["armed"],
        )
        new_sched = {"1": {"start": "08:00", "end": "16:00"}}
        updated = await service.update_position(pos.id, day_schedules=new_sched)

        assert updated.day_schedules == new_sched
        assert updated.name == "ארנונה"  # untouched
        assert updated.required_attributes == ["armed"]  # untouched

    async def test_delete(self, service, db_session):
        profile = await _make_profile(db_session)
        pos = await service.create_position(profile.id, "ארנונה")
        await service.delete_position(pos.id)
        assert await service.list_positions(profile.id) == []

    async def test_get_missing_raises(self, service):
        with pytest.raises(PositionNotFoundException):
            await service.get_position(uuid.uuid4())

    async def test_delete_missing_raises(self, service):
        with pytest.raises(PositionNotFoundException):
            await service.delete_position(uuid.uuid4())
