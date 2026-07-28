from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from services.database.models.room_time_slot import RoomTimeSlotModel

async def room_time_slot_exists(session: AsyncSession, room_id: UUID, time_slot_id: UUID) -> bool:
    result = await session.execute(
        select(RoomTimeSlotModel).where(RoomTimeSlotModel.room_id == room_id, RoomTimeSlotModel.time_slot_id == time_slot_id)
    )
    return result.scalar_one_or_none() is not None

async def create_room_time_slot(session: AsyncSession, room_id: UUID, time_slot_id: UUID) -> RoomTimeSlotModel:
    new_record = RoomTimeSlotModel(room_id=room_id, time_slot_id=time_slot_id)
    session.add(new_record)
    await session.commit()
    await session.refresh(new_record)
    return new_record