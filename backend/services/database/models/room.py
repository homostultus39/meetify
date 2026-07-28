from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from services.database.models.base import Base
from services.database.mixins import TimestampMixin, UUIDMixin


class RoomModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "rooms"
    
    room_number: Mapped[int] = mapped_column(Integer, unique=True, index=True)