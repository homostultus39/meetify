from datetime import date
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.types import UUID, Date
from sqlalchemy.orm import Mapped, mapped_column

from services.database.mixins import UUIDMixin, TimestampMixin
from services.database.models.base import Base


class BookingModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "booking"
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    room_id: Mapped[UUID] = mapped_column(ForeignKey("rooms.id"), nullable=False, index=True)
    time_slot_id: Mapped[UUID] = mapped_column(ForeignKey("time_slots.id"), nullable=False, index=True)
    booking_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("room_id", "booking_date", "time_slot_id", name="uq_room_date_slot"),
    )