from datetime import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.database.models.time_slot import TimeSlotModel


async def get_all_time_slots(session: AsyncSession):
    result = await session.execute(select(TimeSlotModel))
    return list(result.scalars().all())

async def time_slot_exists(session: AsyncSession, start_time: time, end_time: time) -> bool:
    result = await session.execute(
        select(TimeSlotModel).where(
            TimeSlotModel.start_time == start_time,
            TimeSlotModel.end_time == end_time
        )
    )
    return result.scalars().first() is not None

async def create_time_slot(session: AsyncSession, start_time: time, end_time: time) -> TimeSlotModel:
    new_record = TimeSlotModel(
        start_time=start_time,
        end_time=end_time
    )
    session.add(new_record)
    await session.commit()
    await session.refresh(new_record)
    return new_record