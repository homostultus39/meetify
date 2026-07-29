from services.database.connection import sessionmaker
from services.database.logger import logger
from services.database.operations.room import create_new_room, room_exists


async def seed_rooms() -> None:
    room_numbers = [1, 2, 3, 4, 5]

    async with sessionmaker() as session:
        for room_number in room_numbers:
            if await room_exists(session, room_number):
                logger.info(f"Room {room_number} already exists. Skipping.")
            else:
                logger.info(f"Adding room {room_number}.")
                await create_new_room(session, room_number=room_number)
    
        logger.info("Finished seeding rooms.")
