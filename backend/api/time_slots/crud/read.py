from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import DBAPIError

from api.deps.get_current_user import get_current_user
from services.database.connection import SessionDep
from services.database.operations.time_slot import get_all_time_slots
from api.time_slots.schemas import TimeSlotsResponseSchema
from api.time_slots.logger import logger


router = APIRouter()

@router.get("/", response_model=List[TimeSlotsResponseSchema])
async def get_time_slots(session: SessionDep, user = Depends(get_current_user)):
    """
    Получить список всех временных слотов
    """
    try:
        time_slots = await get_all_time_slots(session)
        return [
            TimeSlotsResponseSchema(
                id=time_slot.id,
                start_time=time_slot.start_time,
                end_time=time_slot.end_time
            )
            for time_slot in time_slots
        ]
    except DBAPIError as e:
        logger.error(f"Database error while fetching time slots: {e}")
        raise HTTPException(status_code=500, detail="Database error")