from datetime import time

from sqlalchemy import Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from services.database.mixins import TimestampMixin, UUIDMixin
from services.database.models.base import Base


class TimeSlotModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "time_slots"

    start_time: Mapped[time] = mapped_column(Time, nullable=False, index=True)
    end_time: Mapped[time] = mapped_column(Time, nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("start_time", "end_time", name="uq_start_end"),
    )