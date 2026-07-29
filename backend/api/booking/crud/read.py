
from fastapi import APIRouter, Depends

from api.booking.schemas import BookingResponseScheme
from api.deps.get_current_user import get_current_user
from api.deps.require_role import require_role
from services.database.connection import SessionDep
from services.database.enums.user_roles import UserRoles
from services.database.operations.booking import (
    get_all_booking_records,
    get_users_booking,
)

router = APIRouter()

@router.get("/", response_model=list[BookingResponseScheme])
async def get_all_records(session: SessionDep, user = Depends(require_role(UserRoles.ADMIN))):
    """
    Получить все записи
    """
    booking_records = await get_all_booking_records(session)
    return [
        BookingResponseScheme(
            id = booking.id,
            user_id= booking.user_id,
            room_id= booking.room_id,
            time_slot_id= booking.time_slot_id,
            booking_date= booking.booking_date
        )
        for booking in booking_records
    ]

@router.get("/users", response_model=list[BookingResponseScheme])
async def get_users_records(session: SessionDep, user = Depends(get_current_user)):
    """
    Получить записи пользователя
    """
    users_booking = await get_users_booking(session, user.get("user_id"))
    return [
        BookingResponseScheme(
            id = booking.id,
            user_id= booking.user_id,
            room_id= booking.room_id,
            time_slot_id= booking.time_slot_id,
            booking_date= booking.booking_date
        )
        for booking in users_booking
    ]