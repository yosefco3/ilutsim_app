"""
Tests for ProfileService (part B — schedule builder).
"""

import pytest

from app.exceptions import ProfileDeleteBlockedException, ProfileNotFoundException
from app.schedule_builder.repositories.profile_repository import ProfileRepository
from app.schedule_builder.services.profile_service import (
    DEFAULT_PROFILE_NAME,
    ProfileService,
)


@pytest.fixture
def service(db_session):
    return ProfileService(ProfileRepository(db_session))


class TestCreateAndList:
    async def test_create_then_list_ordered(self, service):
        await service.create_profile("שגרה")
        await service.create_profile("חג", kind="חג", description="ימי חג")
        profiles = await service.list_profiles()

        assert [p.name for p in profiles] == ["שגרה", "חג"]
        assert profiles[1].kind == "חג"
        assert profiles[1].description == "ימי חג"
        # display_order is appended (1, then 2)
        assert profiles[0].display_order < profiles[1].display_order
        assert all(p.is_default is False for p in profiles)

    async def test_get_missing_raises(self, service):
        import uuid

        with pytest.raises(ProfileNotFoundException):
            await service.get_profile(uuid.uuid4())


class TestDuplicate:
    async def test_duplicate_copies_meta_not_default(self, service):
        src = await service.create_profile("שגרה", kind="שגרה", description="בסיס")
        dup = await service.duplicate_profile(src.id)

        assert dup.id != src.id
        assert dup.name == "שגרה (עותק)"
        assert dup.kind == "שגרה"
        assert dup.description == "בסיס"
        assert dup.is_default is False

    async def test_duplicate_with_explicit_name(self, service):
        src = await service.create_profile("שגרה")
        dup = await service.duplicate_profile(src.id, new_name="חג שני")
        assert dup.name == "חג שני"

    async def test_duplicate_deep_copies_positions(self, service, db_session):
        from app.constants import ShiftType
        from app.schedule_builder.repositories.position_repository import (
            PositionRepository,
        )
        from app.schedule_builder.services.position_service import PositionService

        positions = PositionService(PositionRepository(db_session))
        src = await service.create_profile("שגרה")
        await positions.create_position(
            src.id, "ארנונה", ShiftType.MORNING,
            day_schedules={"0": {"start": "07:30", "end": "15:00"}},
            required_attributes=["armed"],
        )
        await positions.create_position(src.id, "קומה 6", ShiftType.NIGHT)

        dup = await service.duplicate_profile(src.id)
        copied = await positions.list_positions(dup.id)
        original = await positions.list_positions(src.id)

        # Two NEW positions under the copy, same content, different ids.
        assert len(copied) == 2
        assert {p.name for p in copied} == {"ארנונה", "קומה 6"}
        assert {p.id for p in copied}.isdisjoint({p.id for p in original})

        # JSON is copied, not shared: mutating the copy must not touch the source.
        arnona_copy = next(p for p in copied if p.name == "ארנונה")
        arnona_copy.day_schedules["0"]["start"] = "09:00"
        arnona_src = next(p for p in original if p.name == "ארנונה")
        assert arnona_src.day_schedules["0"]["start"] == "07:30"


class TestRename:
    async def test_rename_updates_fields_only(self, service):
        p = await service.create_profile("שגרה")
        updated = await service.rename_profile(
            p.id, name="שגרה מעודכנת", kind="שגרה"
        )
        assert updated.name == "שגרה מעודכנת"
        assert updated.kind == "שגרה"

    async def test_rename_does_not_touch_is_default(self, service, db_session):
        # seed creates a default profile
        await service.seed_default_profile()
        default = await ProfileRepository(db_session).get_default()
        assert default is not None
        updated = await service.rename_profile(default.id, name="שגרה ראשית")
        assert updated.is_default is True
        assert updated.name == "שגרה ראשית"


class TestDelete:
    async def test_delete_normal(self, service):
        await service.create_profile("שגרה")
        target = await service.create_profile("חג")
        await service.delete_profile(target.id)
        remaining = await service.list_profiles()
        assert [p.name for p in remaining] == ["שגרה"]

    async def test_delete_last_profile_blocked(self, service):
        only = await service.create_profile("שגרה")
        with pytest.raises(ProfileDeleteBlockedException):
            await service.delete_profile(only.id)


class TestSeed:
    async def test_seed_creates_default_once(self, service):
        await service.seed_default_profile()
        profiles = await service.list_profiles()
        assert len(profiles) == 1
        assert profiles[0].name == DEFAULT_PROFILE_NAME
        assert profiles[0].is_default is True

    async def test_seed_idempotent(self, service):
        await service.seed_default_profile()
        await service.seed_default_profile()
        profiles = await service.list_profiles()
        assert len(profiles) == 1
