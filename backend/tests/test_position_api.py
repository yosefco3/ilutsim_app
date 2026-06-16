"""
Tests for the positions API (part B — schedule builder).

Controller-layer tests with an in-memory fake service (the real service+DB is
covered in test_position_service.py) and ``require_admin_role`` overridden.
"""

import uuid
from datetime import datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.constants import ShiftType
from app.dependencies import require_admin_role
from app.exceptions import PositionNotFoundException
from app.schedule_builder.controllers.position_controller import router as position_router
from app.schedule_builder.dependencies import get_position_service
from app.schedule_builder.models.position import Position

VALID_SCHEDULE = {"0": {"start": "07:30", "end": "15:00"}}


class FakePositionService:
    def __init__(self):
        self._positions: list[Position] = []

    def _make(self, profile_id, name, shift, day_schedules, required_attributes):
        p = Position(
            profile_id=profile_id, name=name, shift=shift,
            day_schedules=day_schedules or {},
            required_attributes=required_attributes or [],
            display_order=len(self._positions),
        )
        p.id = uuid.uuid4()
        p.created_at = datetime(2026, 1, 1)
        return p

    async def list_positions(self, profile_id):
        return [p for p in self._positions if p.profile_id == profile_id]

    async def create_position(self, profile_id, name, shift, day_schedules=None, required_attributes=None):
        p = self._make(profile_id, name, shift, day_schedules, required_attributes)
        self._positions.append(p)
        return p

    def _find(self, pid):
        for p in self._positions:
            if p.id == pid:
                return p
        raise PositionNotFoundException()

    async def get_position(self, pid):
        return self._find(pid)

    async def update_position(self, pid, name=None, shift=None, day_schedules=None, required_attributes=None):
        p = self._find(pid)
        if name is not None:
            p.name = name
        if shift is not None:
            p.shift = shift
        if day_schedules is not None:
            p.day_schedules = day_schedules
        if required_attributes is not None:
            p.required_attributes = required_attributes
        return p

    async def delete_position(self, pid):
        self._positions.remove(self._find(pid))


def _make_client(service):
    app = FastAPI()
    app.include_router(position_router)
    app.dependency_overrides[get_position_service] = lambda: service
    app.dependency_overrides[require_admin_role] = lambda: None
    return TestClient(app)


class TestPositionAPI:
    def test_create_then_list(self):
        svc = FakePositionService()
        client = _make_client(svc)
        profile_id = uuid.uuid4()

        resp = client.post(
            f"/admin/builder/profiles/{profile_id}/positions",
            json={"name": "ארנונה", "shift": "morning",
                  "day_schedules": VALID_SCHEDULE, "required_attributes": ["armed"]},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == "ארנונה"
        assert body["shift"] == "morning"
        assert body["day_schedules"] == VALID_SCHEDULE
        assert body["required_attributes"] == ["armed"]

        resp = client.get(f"/admin/builder/profiles/{profile_id}/positions")
        assert [p["name"] for p in resp.json()] == ["ארנונה"]

    def test_create_bad_day_index_422(self):
        client = _make_client(FakePositionService())
        resp = client.post(
            f"/admin/builder/profiles/{uuid.uuid4()}/positions",
            json={"name": "x", "shift": "morning",
                  "day_schedules": {"9": {"start": "07:00", "end": "15:00"}}},
        )
        assert resp.status_code == 422

    def test_create_bad_time_422(self):
        client = _make_client(FakePositionService())
        resp = client.post(
            f"/admin/builder/profiles/{uuid.uuid4()}/positions",
            json={"name": "x", "shift": "morning",
                  "day_schedules": {"0": {"start": "25:00", "end": "15:00"}}},
        )
        assert resp.status_code == 422

    def test_create_empty_schedule_422(self):
        client = _make_client(FakePositionService())
        resp = client.post(
            f"/admin/builder/profiles/{uuid.uuid4()}/positions",
            json={"name": "x", "shift": "morning", "day_schedules": {}},
        )
        assert resp.status_code == 422

    def test_night_wrap_allowed(self):
        client = _make_client(FakePositionService())
        resp = client.post(
            f"/admin/builder/profiles/{uuid.uuid4()}/positions",
            json={"name": "רכב סיור", "shift": "night",
                  "day_schedules": {"0": {"start": "23:00", "end": "07:00"}}},
        )
        assert resp.status_code == 201

    def test_patch_updates(self):
        svc = FakePositionService()
        p = svc._make(uuid.uuid4(), "ארנונה", ShiftType.MORNING, VALID_SCHEDULE, [])
        svc._positions.append(p)
        client = _make_client(svc)
        resp = client.patch(f"/admin/builder/positions/{p.id}", json={"name": "ארנונה ב"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "ארנונה ב"

    def test_patch_empty_422(self):
        svc = FakePositionService()
        p = svc._make(uuid.uuid4(), "ארנונה", ShiftType.MORNING, VALID_SCHEDULE, [])
        svc._positions.append(p)
        client = _make_client(svc)
        resp = client.patch(f"/admin/builder/positions/{p.id}", json={})
        assert resp.status_code == 422

    def test_get_missing_404(self):
        client = _make_client(FakePositionService())
        resp = client.get(f"/admin/builder/positions/{uuid.uuid4()}")
        assert resp.status_code == 404

    def test_delete_ok(self):
        svc = FakePositionService()
        p = svc._make(uuid.uuid4(), "ארנונה", ShiftType.MORNING, VALID_SCHEDULE, [])
        svc._positions.append(p)
        client = _make_client(svc)
        resp = client.delete(f"/admin/builder/positions/{p.id}")
        assert resp.status_code == 204


class TestPositionAPIAuth:
    def test_requires_admin(self):
        app = FastAPI()
        app.include_router(position_router)
        app.dependency_overrides[get_position_service] = lambda: FakePositionService()
        client = TestClient(app)
        resp = client.get(f"/admin/builder/profiles/{uuid.uuid4()}/positions")
        assert resp.status_code in (401, 403)
