from datetime import time
from uuid import UUID

from pydantic import BaseModel


class RoomsResponseSchema(BaseModel):
    id: UUID
    room_number: int

class TimeSlotAvailabilityScheme(BaseModel):
    time_slot_id: UUID
    start_time: time
    end_time: time
    is_available: bool

class RoomAvailabilityScheme(BaseModel):
    room_id: UUID
    room_number: int
    slots: list[TimeSlotAvailabilityScheme]