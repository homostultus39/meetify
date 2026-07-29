from fastapi import APIRouter

from api.booking.crud import create_router, delete_router, read_router

router = APIRouter(prefix="/booking", tags=["Booking"])

router.include_router(create_router)
router.include_router(read_router)
router.include_router(delete_router)