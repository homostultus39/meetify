from datetime import date
from uuid import UUID

from pydantic import BaseModel


class BookingResponseScheme(BaseModel):
    id: UUID
    user_id: UUID
    room_id: UUID
    time_slot_id: UUID
    booking_date: date

class BookingCreateResponseScheme(BaseModel):
    id: UUID
    user_id: UUID
    room_id: UUID
    time_slot_id: UUID
    booking_date: date
    success: bool = True

class BookingCreateScheme(BaseModel):
    user_id: UUID
    room_id: UUID
    time_slot_id: UUID
    booking_date: date