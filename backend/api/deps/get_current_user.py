
from fastapi import HTTPException
from fastapi.params import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.auth.management.token_service import TokenService
from api.exceptions.user import UserNotFoundError
from services.database.connection import SessionDep
from services.database.operations.user import get_user_by_user_id

security = HTTPBearer(scheme_name="Bearer", description="Access token for authentication")

async def get_current_user(session: SessionDep, credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    token = credentials.credentials
    payload = TokenService.decode_token(token)
        
    if payload["type"] != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = payload["sub"]
    user_record = await get_user_by_user_id(session, user_id)

    if not user_record:
        raise UserNotFoundError(f"User with id {user_id} not found")
        
    return {
        "user_id": user_record.id,
        "username": user_record.username,
        "role": user_record.role
    }