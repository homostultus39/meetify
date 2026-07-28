from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from api.deps.get_current_user import get_current_user
from services.database.connection import SessionDep
from services.database.operations.booking import create_record
from api.booking.schemas import BookingCreateScheme, BookingCreateResponseScheme
from api.booking.logger import logger


router = APIRouter()


@router.post("/", response_model=BookingCreateResponseScheme)
async def create_booking_record(session: SessionDep, booking_data: BookingCreateScheme, user = Depends(get_current_user)):
    """
    Создать запись с бронью
    """
    try:
        booking = await create_record(
            session,
            booking_data.user_id,
            booking_data.room_id,
            booking_data.time_slot_id,
            booking_data.booking_date
        )
        return BookingCreateResponseScheme(
            id = booking.id,
            user_id = booking.user_id,
            room_id = booking.room_id,
            time_slot_id = booking.time_slot_id,
            booking_date = booking.booking_date
        )
    except IntegrityError:
        logger.warning(f"Attempt creating booking record with same fields room_id={booking_data.room_id}, time_slot_id={booking_data.time_slot_id}, booking_date={booking_data.booking_date}")
        raise HTTPException(status_code=400, detail="Record with same fields already existst")