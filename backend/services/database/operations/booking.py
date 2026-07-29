from datetime import date
from uuid import UUID

from sqlalchemy import select

from services.database.connection import AsyncSession
from services.database.models.booking import BookingModel


async def create_record(
        session: AsyncSession,
        user_id: UUID,
        room_id: UUID,
        time_slot_id: UUID,
        booking_date: date
) -> BookingModel:
    new_booking = BookingModel(
        user_id=user_id,
        room_id=room_id,
        time_slot_id=time_slot_id,
        booking_date=booking_date
    )
    session.add(new_booking)
    await session.commit()
    await session.refresh(new_booking)
    return new_booking

async def get_all_booking_records(session: AsyncSession) -> list[BookingModel]:
    result = await session.execute(select(BookingModel))
    return list(result.scalars().all())

async def get_users_booking(session: AsyncSession, user_id: UUID) -> list[BookingModel]:
    result = await session.execute(select(BookingModel).where(BookingModel.user_id == user_id))
    return list(result.scalars().all())

async def get_booking_by_id(session: AsyncSession, booking_id: UUID) -> BookingModel | None:
    result = await session.execute(select(BookingModel).where(BookingModel.id == booking_id))
    return result.scalars().one_or_none()

async def delete_record(session: AsyncSession, booking: BookingModel) -> None:
    await session.delete(booking)
    await session.commit()