from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid import uuid4

class UUIDMixin:
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )