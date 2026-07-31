from fastapi import Depends

from api.deps.get_current_user import get_current_user
from api.deps.logger import logger
from api.exceptions.permission import PermissionDeniedError
from services.database.enums.user_roles import UserRoles


def require_role(*allowed_roles: UserRoles):
    async def role_checker(user = Depends(get_current_user)) -> dict:
        user_role = user["role"] if isinstance(user["role"], UserRoles) else UserRoles(user["role"])
        if user_role not in allowed_roles:
            logger.warning(f"User {user.get('username')} attempted to access restricted resource.")
            raise PermissionDeniedError("Insufficient permissions")
        return user
    return role_checker