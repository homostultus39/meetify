from fastapi import APIRouter, Depends

from api.booking.schemas import BookingCreateResponseScheme, BookingCreateScheme
from api.deps.get_current_user import get_current_user
from services.database.connection import SessionDep
from services.database.operations.booking import create_record

router = APIRouter()


@router.post("/", response_model=BookingCreateResponseScheme)
async def create_booking_record(session: SessionDep, booking_data: BookingCreateScheme, user = Depends(get_current_user)):
    """
    Создать запись с бронью
    """
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