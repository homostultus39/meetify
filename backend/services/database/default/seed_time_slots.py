from datetime import date, datetime, time, timedelta

from services.database.connection import sessionmaker
from services.database.logger import logger
from services.database.operations.time_slot import time_slot_exists, create_time_slot


async def seed_time_slots() -> None:
    start_time = time(9, 0)
    end_time = time(18, 0)
    interval = timedelta(hours=2)

    current_time = start_time
    async with sessionmaker() as session:
        while current_time < end_time:
            next_time = (datetime.combine(date.today(), current_time) + interval).time()
            if await time_slot_exists(session, current_time, next_time):
                logger.info(f"Time slot {current_time} - {next_time} already exists. Skipping.")
            else:
                await create_time_slot(session, current_time, next_time)
            current_time = next_time