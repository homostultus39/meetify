from api.rooms.crud import read_router

from fastapi import APIRouter


router = APIRouter(prefix="/rooms", tags=["Rooms"])
router.include_router(read_router)