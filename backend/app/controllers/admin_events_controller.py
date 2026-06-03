"""
AdminEventsController — admin endpoints for schedule events.
"""

import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_event_service, require_admin_role
from app.schemas.event_schemas import EventCreate, EventResponse, EventUpdate
from app.services.event_service import EventService

logger = logging.getLogger("ilutzim")

router = APIRouter(
    prefix="/admin/events",
    tags=["Admin – Events"],
    dependencies=[Depends(require_admin_role)],
)


@router.get("/week/{week_id}", response_model=list[EventResponse])
async def get_events_for_week(
    week_id: uuid.UUID,
    event_service: EventService = Depends(get_event_service),
):
    """Get all events for a specific week."""
    return await event_service.get_events_for_week(week_id)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: uuid.UUID,
    event_service: EventService = Depends(get_event_service),
):
    """Get a single event by ID."""
    event = await event_service.get_event(event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    return event


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    data: EventCreate,
    event_service: EventService = Depends(get_event_service),
):
    """Create a new schedule event."""
    try:
        return await event_service.create_event(data)
    except Exception as e:
        logger.error(f"Event creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: uuid.UUID,
    data: EventUpdate,
    event_service: EventService = Depends(get_event_service),
):
    """Update an existing schedule event."""
    try:
        event = await event_service.update_event(event_id, data)
        if event is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )
        return event
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Event update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: uuid.UUID,
    event_service: EventService = Depends(get_event_service),
):
    """Delete a schedule event."""
    success = await event_service.delete_event(event_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )