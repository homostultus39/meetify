from fastapi import APIRouter, Request, Response

from api.auth.logger import logger
from api.auth.management.pwd_manager import PWDManager
from api.auth.management.token_service import TokenService
from api.auth.schemas import LoginScheme, TokenResponseScheme
from api.exceptions.auth import (
    InvalidCredentialsError,
    RefreshTokenMissing,
    TokenExpiredError,
    TokenInvalidError,
)
from api.exceptions.user import UserNotFoundError
from management.settings import get_settings
from services.database.connection import SessionDep
from services.database.operations.user import get_user_by_user_id, get_user_by_username
from services.redis.operations.token_denylist_repo import TokenRepository

router = APIRouter(prefix="/auth", tags=["Authorization"])
settings = get_settings()


@router.post("/login", response_model=TokenResponseScheme)
async def login(session: SessionDep, credentials: LoginScheme, response: Response):
    """
    Аутентификация
    """
    username = credentials.username
    password = credentials.password
    
    existing_user = await get_user_by_username(session, username)
    
    if not existing_user:
        logger.info(f"Failed login attempt for username {credentials.username}")
        raise InvalidCredentialsError("Invalid username or password")

    if not PWDManager.check_password(password, existing_user.password_hash):
        logger.info(f"Failed login attempt for username {username}")
        raise InvalidCredentialsError("Invalid username or password")

    logger.info(f"User with username {username} logged in succesfully")
    token_pair = await TokenService.reset_token_pair(user=existing_user)

    response.set_cookie(
        key = "refresh_token",
        value = token_pair["refresh_token"],
        httponly = True,
        secure = settings.cookie_secure,
        samesite = settings.cookie_samesite
    )

    return TokenResponseScheme(
        access_token=token_pair["access_token"]
    )

@router.post("/refresh", response_model=TokenResponseScheme)
async def refresh_token(session: SessionDep, request: Request, response: Response):
    """
    Обновление пары токенов
    """
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise RefreshTokenMissing("Refresh token missing")
    
    payload = TokenService.decode_token(refresh_token)
    
    user_id = payload["sub"]

    if payload["type"] != "refresh":
        raise TokenInvalidError("Invalid type of token")
    
    if await TokenRepository.exists(payload["jti"]):
        raise TokenExpiredError("Token has expired")
    
    user_record = await get_user_by_user_id(session, user_id)
    if not user_record:
        raise UserNotFoundError(f"User {payload['sub']} not found")

    token_pair = await TokenService.reset_token_pair(user=user_record, exp_refresh_token=refresh_token)

    response.set_cookie(
        key = "refresh_token",
        value = token_pair["refresh_token"],
        httponly = True,
        secure = settings.cookie_secure,
        samesite = settings.cookie_samesite
    )
    return TokenResponseScheme(
        access_token=token_pair["access_token"]
    )
        

@router.post("/logout")
async def logout(request: Request, response: Response):
    """
    Выход из аккаунта
    """
    refresh_token = request.cookies.get("refresh_token")
    try:
        if refresh_token:
            payload = TokenService.decode_token(refresh_token)
            if payload.get("type") == "refresh":
                await TokenService.block_token(exp_refresh_token=refresh_token)
    except Exception as e:
        # энивей, надо перехватить все исключения и удалить куку на клиенте
        logger.warning(f"Error during logout processing: {e}")
    finally:
        response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}