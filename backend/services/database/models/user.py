from sqlalchemy.types import String, Enum
from sqlalchemy.orm import Mapped, mapped_column

from services.database.mixins import UUIDMixin, TimestampMixin
from services.database.enums import UserRoles
from services.database.models.base import Base


class UserModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(60), nullable=False)
    role: Mapped[UserRoles] = mapped_column(Enum(UserRoles), nullable=False, default=UserRoles.STAFF)