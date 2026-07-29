from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from management.settings import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url, echo=False
)

sessionmaker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_session() -> AsyncSession:
    async with sessionmaker() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]