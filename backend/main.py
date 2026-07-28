
from fastapi import FastAPI
from contextlib import asynccontextmanager
from alembic import command
from alembic.config import Config
from fastapi.responses import JSONResponse
from api.auth.exceptions import TokenExpiredError, TokenInvalidError
from management.logger import configure_logger
from management.settings import get_settings
from api.auth import auth_router
from api.time_slots import time_slots_router
from api.rooms import rooms_router
from api.booking import booking_router
from services.database.default import seed_admin, seed_room_time_slots, seed_rooms, seed_time_slots


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
        logger.info("Начинаем seed_admin")
        await seed_admin()
        logger.info("seed_admin завершён")

        logger.info("Начинаем seed_time_slots")
        await seed_time_slots()
        logger.info("seed_time_slots завершён")

        logger.info("Начинаем seed_rooms")
        await seed_rooms()
        logger.info("seed_rooms завершён")

        logger.info("Начинаем seed_room_time_slots")
        await seed_room_time_slots()
        logger.info("seed_room_time_slots завершён")

        logger.info("Инициализация данных завершена.")
    except Exception as e:
        logger.error(f"Ошибка при инициализации данных: {e}", exc_info=True)
        raise  # если хотите, чтобы приложение не стартовало при ошибке

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
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )

@app.exception_handler(TokenExpiredError)
async def token_expired_handler(request, exc):
    return JSONResponse(
        status_code=401,
        content={"message": "Token has expired"},
    )

@app.exception_handler(TokenInvalidError)
async def token_invalid_handler(request, exc):
    logger.warning(
        f"Invalid token attempt on {request.url.path} from {request.client.host} with method {request.method}"
    )
    return JSONResponse(
        status_code=401,
        content={"message": "Invalid token"},
    )

app.include_router(auth_router)
app.include_router(time_slots_router)
app.include_router(rooms_router)
app.include_router(booking_router)