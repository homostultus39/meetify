from fastapi import APIRouter

from api.rooms.crud import read_router

router = APIRouter(prefix="/rooms", tags=["Rooms"])
router.include_router(read_router)