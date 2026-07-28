from fastapi import APIRouter, HTTPException, Response, Request

from api.auth.logger import logger
from api.auth.schemas import LoginScheme, TokenResponseScheme
from services.database.connection import SessionDep
from services.database.operations.user import get_user_by_username, get_user_by_user_id
from api.auth.management.pwd_manager import PWDManager
from api.auth.management.token_service import TokenService
from management.settings import get_settings
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
    
    if existing_user:
        user_verified = PWDManager.check_password(password, existing_user.password_hash)
        if not user_verified:
            logger.info(f"Failed login attempt for username {username}")
            raise HTTPException(status_code=401, detail="Invalid credentials")

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
    else:
        logger.info(f"Failed login attempt for username {username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/refresh", response_model=TokenResponseScheme)
async def refresh_token(session: SessionDep, request: Request, response: Response):
    """
    Обновление пары токенов
    """
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    payload = TokenService.decode_token(refresh_token)
    user_id = payload["sub"]

    if payload["type"] != "refresh":
        raise HTTPException(status_code=401, detail="Invalid type of token")
    
    if await TokenRepository.exists(payload["jti"]):
        raise HTTPException(status_code=401, detail="Provided expired token")
    
    user_record = await get_user_by_user_id(session, user_id)
    
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

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    try:
        payload = TokenService.decode_token(refresh_token)

        if payload["type"] != "refresh":
            raise HTTPException(status_code=401, detail="Invalid type of token")
    
        if await TokenRepository.exists(payload["jti"]):
            raise HTTPException(status_code=401, detail="Provided blocked token")
    
        await TokenService.block_token(exp_refresh_token=refresh_token)
    except HTTPException:
        pass

    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}