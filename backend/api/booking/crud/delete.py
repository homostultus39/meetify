from uuid import UUID

from fastapi import APIRouter, Depends

from api.booking.logger import logger
from api.deps.get_current_user import get_current_user
from api.exceptions.booking import BookingNotFoundError
from api.exceptions.permission import PermissionDeniedError
from services.database.connection import SessionDep
from services.database.enums import UserRoles
from services.database.operations.booking import delete_record, get_booking_by_id

router = APIRouter()


@router.delete("/{booking_id}")
async def delete_booking_record(session: SessionDep, booking_id: UUID, user = Depends(get_current_user)):
    """
    Удалить запись с бронью
    """
    booking = await get_booking_by_id(session, booking_id)
    if booking is None:
        raise BookingNotFoundError(f"Booking {booking_id} not found")
    
    is_owner = booking.user_id == user.get("user_id")
    is_admin = user.get("role") == UserRoles.ADMIN.value
    
    if not (is_owner or is_admin):
        logger.warning(f"User {user.get('user_id')} attempted to delete booking record {booking_id} without permission")
        raise PermissionDeniedError("You do not have permission to delete this booking record")
    
    await delete_record(session, booking)
    return {"message" : f"booking with id {booking_id} successfully deleted"}