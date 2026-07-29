from datetime import date

from fastapi import APIRouter, Depends

from api.deps.get_current_user import get_current_user
from api.rooms.schemas import (
    RoomAvailabilityScheme,
    RoomsResponseSchema,
    TimeSlotAvailabilityScheme,
)
from services.database.connection import SessionDep
from services.database.operations.room import get_all_rooms, get_rooms_availability

router = APIRouter()


@router.get("/", response_model=list[RoomsResponseSchema])
async def get_rooms(session: SessionDep, user = Depends(get_current_user)):
    """
    Получить список всех комнат в системе
    """
    all_rooms = await get_all_rooms(session)
    return [
        RoomsResponseSchema(
            id=room.id,
            room_number=room.room_number
        )
        for room in all_rooms
    ]


@router.get("/availability", response_model=list[RoomAvailabilityScheme])
async def get_rooms_availabilities(session: SessionDep, target_date: date, user = Depends(get_current_user)):
    """
    Получить доступность всех комнат
    """
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