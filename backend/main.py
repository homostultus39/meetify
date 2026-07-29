
from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError, IntegrityError, OperationalError

from api.auth import auth_router
from api.booking import booking_router
from api.exceptions.auth import (
    InvalidCredentialsError,
    RefreshTokenMissing,
    TokenExpiredError,
    TokenInvalidError,
)
from api.exceptions.booking import BookingNotFoundError
from api.exceptions.permission import PermissionDeniedError
from api.exceptions.user import UserNotFoundError
from api.rooms import rooms_router
from api.time_slots import time_slots_router
from management.logger import configure_logger
from management.settings import get_settings
from services.database.default import (
    seed_admin,
    seed_room_time_slots,
    seed_rooms,
    seed_time_slots,
)

settings = get_settings()
logger = configure_logger("MAIN")


def run_migrations():
    logger.info("Миграции запускаются...")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    logger.info("Миграции успешно применены.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    try:
        await seed_admin()
        await seed_time_slots()
        await seed_rooms()
        await seed_room_time_slots()

        logger.info("Инициализация данных завершена.")
    except Exception as e:
        logger.exception(f"Ошибка при инициализации данных: {e}")
        raise

    yield
    logger.info("Работа сервиса завершена.")


app = FastAPI(
    title="meetify",
    description="service for booking meeting rooms",
    root_path="/api/v1",
    docs_url="/docs" if settings.development else None,
    redoc_url="/redoc" if settings.development else None,
    openapi_url="/openapi.json" if settings.development else None,
    swagger_ui_parameters={"persistAuthorization": True},
    lifespan=lifespan
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

@app.exception_handler(TokenExpiredError)
async def token_expired_handler(request: Request, exc: TokenExpiredError):
    logger.warning(f"Expired token used on {request.url.path}")
    return JSONResponse(
        status_code=401,
        content={"detail": "Token has expired"},
    )

@app.exception_handler(TokenInvalidError)
async def token_invalid_handler(request: Request, exc: TokenInvalidError):
    logger.warning(
        f"Invalid token attempt on {request.url.path} from {request.client.host}"
    )
    return JSONResponse(
        status_code=401,
        content={"detail": "Invalid token"},
    )

@app.exception_handler(PermissionDeniedError)
async def permission_denied_handler(request: Request, exc: PermissionDeniedError):
    logger.warning(
        f"Permission denied on {request.url.path}: {exc}"
    )
    return JSONResponse(
        status_code=403,
        content={"detail": "You don't have right permission for this operation"},
    )

@app.exception_handler(BookingNotFoundError)
async def booking_not_found_handler(request: Request, exc: BookingNotFoundError):
    logger.warning(f"Booking not found: {exc}")
    return JSONResponse(
        status_code=404,
        content={"detail": "Booking record does not exist"}
    )

@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    logger.warning(f"User not found: {exc}")
    return JSONResponse(status_code=404, content={"detail": "User not found"})

@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError):
    logger.warning(f"Invalid login attempt on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=401,
        content={"detail": "Invalid credentials"},
    )

@app.exception_handler(RefreshTokenMissing)
async def refresh_token_missing_handler(request: Request, exc: RefreshTokenMissing):
    logger.warning(f"Refresh token missing on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=401,
        content={"detail": "Refresh token missing"},
    )

@app.exception_handler(IntegrityError)
async def duplicate_db_error(request: Request, exc: IntegrityError):
    logger.warning(f"Integrity error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=409,
        content={"detail": "Record already exists or violates constraints"},
    )

@app.exception_handler(OperationalError) 
async def operational_error_handler(request: Request, exc: OperationalError):
    logger.error(f"Database operational error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=503,
        content={"detail": "Database service temporarily unavailable"},
    )

@app.exception_handler(DBAPIError)
async def dbapi_error_handler(request: Request, exc: DBAPIError):
    logger.error(f"Database API error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal database error"},
    )

app.include_router(auth_router)
app.include_router(time_slots_router)
app.include_router(rooms_router)
app.include_router(booking_router)