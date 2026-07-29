
from fastapi import APIRouter, Depends

from api.deps.get_current_user import get_current_user
from api.time_slots.schemas import TimeSlotsResponseSchema
from services.database.connection import SessionDep
from services.database.operations.time_slot import get_all_time_slots

router = APIRouter()

@router.get("/", response_model=list[TimeSlotsResponseSchema])
async def get_time_slots(session: SessionDep, user = Depends(get_current_user)):
    """
    Получить список всех временных слотов
    """
    time_slots = await get_all_time_slots(session)
    return [
        TimeSlotsResponseSchema(
            id=time_slot.id,
            start_time=time_slot.start_time,
            end_time=time_slot.end_time
        )
        for time_slot in time_slots
    ]