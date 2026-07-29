from datetime import time
from uuid import UUID

from pydantic import BaseModel


class TimeSlotsResponseSchema(BaseModel):
    id: UUID
    start_time: time
    end_time: time