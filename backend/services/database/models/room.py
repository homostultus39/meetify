from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from services.database.mixins import TimestampMixin, UUIDMixin
from services.database.models.base import Base


class RoomModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "rooms"
    
    room_number: Mapped[int] = mapped_column(Integer, unique=True, index=True)