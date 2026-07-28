from fastapi import APIRouter
from api.time_slots.crud import read_router


router = APIRouter(prefix="/time_slots", tags=["Time slots"])
router.include_router(read_router)