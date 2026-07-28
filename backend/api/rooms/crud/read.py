from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import DBAPIError
from datetime import date

from api.deps.get_current_user import get_current_user
from services.database.connection import SessionDep
from services.database.operations.room import get_all_rooms, get_rooms_availability
from api.rooms.schemas import RoomsResponseSchema, RoomAvailabilityScheme, TimeSlotAvailabilityScheme
from api.rooms.logger import logger


router = APIRouter()


@router.get("/", response_model=List[RoomsResponseSchema])
async def get_rooms(session: SessionDep, user = Depends(get_current_user)):
    """
    Получить список всех комнат в системе
    """
    try:
        all_rooms = await get_all_rooms(session)
        return [
            RoomsResponseSchema(
                id=room.id,
                room_number=room.room_number
            )
            for room in all_rooms
        ]
    except DBAPIError as e:
        logger.error(f"Database error while fetching rooms: {e}")
        raise HTTPException(status_code=500, detail="Database error")

@router.get("/availability", response_model=List[RoomAvailabilityScheme])
async def get_rooms_availabilities(session: SessionDep, target_date: date, user = Depends(get_current_user)):
    """
    Получить доступность всех комнат
    """
    try:
        rooms_availability = await get_rooms_availability(session, target_date)
        return [
            RoomAvailabilityScheme(
                room_id=room.id,
                room_number=room.room_number,
                slots=[
                    TimeSlotAvailabilityScheme(
                        time_slot_id=slot.id,
                        start_time=slot.start_time,
                        end_time=slot.end_time,
                        is_available=slot.is_available
                    )
                    for slot in room.get("slots", [])
                ]
            )
            for room in rooms_availability
        ]
    except DBAPIError as e:
        logger.error(f"Database error while fetching rooms statuses: {e}")
        raise HTTPException(status_code=500, detail="Database error")