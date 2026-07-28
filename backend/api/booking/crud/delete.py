from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import DBAPIError
from uuid import UUID

from api.deps.get_current_user import get_current_user
from services.database.connection import SessionDep
from services.database.enums import UserRoles
from services.database.operations.booking import delete_record, get_booking_by_id
from api.booking.logger import logger


router = APIRouter()


@router.delete("/{booking_id}")
async def delete_booking_record(session: SessionDep, booking_id: UUID, user = Depends(get_current_user)):
    """
    Удалить запись с бронью
    """
    try:
        booking = await get_booking_by_id(session, booking_id)
        if booking is None:
            raise HTTPException(status_code=404, detail="Booking record not found")
        
        is_owner = booking.user_id == user.get("user_id")
        is_admin = user.get("role") == UserRoles.ADMIN.value
        
        if not (is_owner or is_admin):
            logger.warning(f"User {user.get('user_id')} attempted to delete booking record {booking_id} without permission")
            raise HTTPException(status_code=403, detail="You do not have permission to delete this booking record")
        

        await delete_record(session, booking)
        return {"message" : f"booking with id {booking_id} successfully deleted"}
    except DBAPIError:
        logger.warning(f"Database error occurred while attempting to delete booking record {booking_id}")
        raise HTTPException(status_code=500, detail="Database error")