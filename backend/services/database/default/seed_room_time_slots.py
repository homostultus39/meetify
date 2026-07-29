from sqlalchemy import select

from services.database.connection import sessionmaker
from services.database.logger import logger
from services.database.models.room import RoomModel
from services.database.models.time_slot import TimeSlotModel
from services.database.operations.room_time_slot import (
    create_room_time_slot,
    room_time_slot_exists,
)


async def seed_room_time_slots() -> None:
    async with sessionmaker() as session:
        rooms = (await session.execute(select(RoomModel))).scalars().all()
        time_slots = (await session.execute(select(TimeSlotModel))).scalars().all()

        for room in rooms:
            for slot in time_slots:
                if await room_time_slot_exists(session, room.id, slot.id):
                    continue
                logger.info(
                    f"Linking room {room.room_number} to slot {slot.start_time}-{slot.end_time}."
                )
                await create_room_time_slot(session, room_id=room.id, time_slot_id=slot.id)

    logger.info("Finished seeding room-time-slot links.")