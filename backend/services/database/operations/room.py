from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.database.models.booking import BookingModel
from services.database.models.room_time_slot import RoomTimeSlotModel
from services.database.models.time_slot import TimeSlotModel
from services.database.models import RoomModel


async def get_all_rooms(session: AsyncSession) -> list[RoomModel]:
    result = await session.execute(select(RoomModel))
    return list(result.scalars().all())

async def create_new_room(session: AsyncSession, room_number: int) -> RoomModel:
    new_room = RoomModel(room_number=room_number)
    session.add(new_room)
    await session.commit()
    await session.refresh(new_room)
    return new_room

async def get_rooms_availability(session: AsyncSession, target_date: date) -> list[dict]:
    query = await session.execute(
            select(
                RoomModel.id.label("room_id"),
                RoomModel.room_number,
                TimeSlotModel.id.label("time_slot_id"),
                TimeSlotModel.start_time,
                TimeSlotModel.end_time,
                BookingModel.id.label("booking_id")
            )
            .join(RoomTimeSlotModel, RoomTimeSlotModel.room_id == RoomModel.id)
            .join(TimeSlotModel, TimeSlotModel.id == RoomTimeSlotModel.time_slot_id)
            .outerjoin(
                BookingModel,
                and_(
                    BookingModel.room_id == RoomModel.id,
                    BookingModel.time_slot_id == TimeSlotModel.id,
                    BookingModel.booking_date == target_date
                ),
            )
            .order_by(RoomModel.room_number, TimeSlotModel.start_time)
    )
    rows = query.all()

    rooms = {}
    for row in rows:
        room = rooms.setdefault(
            row.room_id,
            {
                "room_id": row.room_id,
                "room_number": row.room_number,
                "slots": [],
            },
        )
        room["slots"].append(
            {
                "time_slot_id": row.time_slot_id,
                "start_time": row.start_time,
                "end_time": row.end_time,
                "is_available": row.booking_id is None,
            }
        )
    return list(rooms.values())

async def room_exists(session: AsyncSession, room_number: int) -> bool:
    result = await session.execute(
        select(RoomModel).where(RoomModel.room_number == room_number)
    )
    return result.scalar_one_or_none() is not None