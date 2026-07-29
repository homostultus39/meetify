from api.booking.crud.create import router as create_router
from api.booking.crud.delete import router as delete_router
from api.booking.crud.read import router as read_router

all = [
    create_router,
    read_router,
    delete_router
]