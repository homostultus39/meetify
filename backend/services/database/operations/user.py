from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.database.models import UserModel
from services.database.enums import UserRoles
from services.database.logger import logger


async def create_user(
        session: AsyncSession,
        username: str,
        password_hash: str,
        role: UserRoles = None
        ) -> None:
    try:
        new_user = UserModel(
            username=username,
            password_hash=password_hash,
            role=role
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        logger.info(f"User {username} was created succesfully")
        return new_user
    except TypeError:
        logger.error(f"Incorrect type of input data while creating user {username}")
        raise

async def get_user_by_username(session: AsyncSession, username: str) -> UserModel | None:
    result = await session.execute(
        select(UserModel).where(UserModel.username == username)
    )
    return result.scalar_one_or_none()

async def get_user_by_user_id(session: AsyncSession, user_id: str) -> UserModel | None:
    result = await session.execute(
        select(UserModel).where(UserModel.id == user_id)
    )
    return result.scalar_one_or_none()