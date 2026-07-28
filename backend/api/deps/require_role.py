from fastapi import Depends, HTTPException

from api.deps.get_current_user import get_current_user
from services.database.enums.user_roles import UserRoles
from api.deps.logger import logger

def require_role(*allowed_roles: UserRoles):
    async def role_checker(user = Depends(get_current_user)) -> dict:
        if user.get("role") not in allowed_roles:
            logger.warning(f"User {user.get('username')} attempted to access restricted resource.")
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker