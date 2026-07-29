from api.auth.management.pwd_manager import PWDManager
from management.settings import get_settings
from services.database.connection import sessionmaker
from services.database.enums import UserRoles
from services.database.logger import logger
from services.database.operations.user import create_user, get_user_by_username


async def seed_admin() -> None:
    settings = get_settings()
    async with sessionmaker() as session:
        existing = await get_user_by_username(session, settings.init_admin_username)
        if not existing:
            await create_user(
                session, settings.init_admin_username, PWDManager.hash_password(settings.init_admin_password), UserRoles.ADMIN
            )
            logger.info("Admin user was succesfully created")