from typing import List

from fastapi import APIRouter, Depends, HTTPException
from services.database.connection import SessionDep
from services.database.enums.user_roles import UserRoles
from services.database.operations.booking import (
    get_all_booking_records,
    get_users_booking,
)
from sqlalchemy.exc import DBAPIError

from api.booking.logger import logger
from api.booking.schemas import BookingResponseScheme
from api.deps.get_current_user import get_current_user
from api.deps.require_role import require_role

router = APIRouter()

@router.get("/", response_model=List[BookingResponseScheme])
async def get_all_records(session: SessionDep, user = Depends(require_role(UserRoles.ADMIN))):
    """
    Получить все записи
    """
    try:
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
    except DBAPIError as e:
        logger.error(f"Database error while fetching time slots: {e}")
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/users", response_model=List[BookingResponseScheme])
async def get_users_records(session: SessionDep, user = Depends(get_current_user)):
    """
    Получить записи пользователя
    """
    try:
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
    except DBAPIError as e:
        logger.error(f"Database error while fetching time slots: {e}")
        raise HTTPException(status_code=500, detail="Database error")