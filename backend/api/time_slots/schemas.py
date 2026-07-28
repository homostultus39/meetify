from datetime import time
from pydantic import BaseModel
from uuid import UUID


class TimeSlotsResponseSchema(BaseModel):
    id: UUID
    start_time: time
    end_time: time