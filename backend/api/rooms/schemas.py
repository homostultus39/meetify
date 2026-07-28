from pydantic import BaseModel
from uuid import UUID
from datetime import time


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