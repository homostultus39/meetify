from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import UUID

from services.database.mixins import TimestampMixin, UUIDMixin
from services.database.models.base import Base


class RoomTimeSlotModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "room_time_slots"

    room_id: Mapped[UUID] = mapped_column(ForeignKey("rooms.id"), nullable=False, index=True)
    time_slot_id: Mapped[UUID] = mapped_column(ForeignKey("time_slots.id"), nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("room_id", "time_slot_id", name="uq_room_slot"),
    )