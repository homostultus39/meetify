import asyncio
import asyncpg
import pytest
from uuid import uuid4
from api.auth.management.token_service import TokenService
from httpx import ASGITransport, AsyncClient
from main import app
from management.settings import get_settings
from services.database.connection import get_session
from services.database.models import Base, UserModel
from services.database.enums import UserRoles
from unittest.mock import MagicMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker


settings = get_settings()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(
        settings.test_database_url,
        future=True,
        echo=False,
    )
    yield engine
    await engine.dispose()

@pytest.fixture(scope="session")
async def async_session_test(async_engine):
    async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
    yield async_session

@pytest.fixture(scope="session") # autouse=True
async def prepare_database(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function") # autouse=True
async def clean_tables(async_session_test):
    tables = [
        "bookings",
        "room_time_slots",
        "rooms",
        "time_slots",
        "users",
    ]
    async with async_session_test() as session:
        for table in tables:
            await session.execute(f"TRUNCATE TABLE {table} CASCADE;")
        await session.commit()

async def _get_test_db_override():
    async with async_session_test() as session:
        yield session

@pytest.fixture(scope="function")
async def async_client():
    app.dependency_overrides[get_session] = _get_test_db_override
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://meetify") as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
async def asyncpg_pool():
    dsn = settings.test_database_url.replace("+asyncpg", "")
    pool = await asyncpg.create_pool(dsn)
    yield pool
    await pool.close()

@pytest.fixture
async def create_user_in_db(asyncpg_pool):
    async def _create_user(user_id, username, password_hash, role):
        async with asyncpg_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (id, username, password_hash, role, created_at, updated_at)
                VALUES ($1, $2, $3, $4, NOW(), NOW())
                """,
                user_id, username, password_hash, role
            )
    return _create_user

@pytest.fixture
async def get_user_from_db(asyncpg_pool):
    async def _get_user(user_id):
        async with asyncpg_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1;", user_id
            )
            return dict(row) if row else None
    return _get_user

async def create_test_access_token(user: UserModel) -> str:
    token_pair = await TokenService.reset_token_pair(user=user)
    return token_pair["access_token"]

async def create_test_auth_headers(user: UserModel) -> dict:
    return {"Authorization": f"Bearer {create_test_access_token(user)}"}

@pytest.fixture
def mock_user_model():
    return UserModel(id=uuid4(), username="testuser", role=UserRoles.ADMIN)

@pytest.fixture
def mock_settings():
    mock = MagicMock()
    mock.secret_key = "a" * 32
    mock.algorithm = "HS256"
    mock.access_token_expire_minutes = 15
    mock.refresh_token_expire_days = 7
    return mock