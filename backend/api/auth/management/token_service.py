import secrets
from datetime import datetime, timedelta

import jwt

from api.exceptions.auth import TokenExpiredError, TokenInvalidError
from management.settings import get_settings
from services.database.models import UserModel
from services.redis.operations.token_denylist_repo import TokenRepository

settings = get_settings()

class TokenService:
    @staticmethod
    def _create_jti() -> str:
        return secrets.token_urlsafe(16)

    @staticmethod
    async def reset_token_pair(user: UserModel, exp_refresh_token: str | None = None) -> dict:
        if exp_refresh_token:
            refresh_payload = TokenService.decode_token(exp_refresh_token)
            
            await TokenRepository.set_record(
                jti=refresh_payload['jti'], 
                ttl_seconds=refresh_payload["exp"]
            )

        access_payload = {
            "sub": str(user.id),
            "role": user.role.value,
            "exp": datetime.now() + timedelta(minutes=settings.access_token_expire_minutes),
            "type": "access",
            "jti": TokenService._create_jti()
        }

        refresh_payload = {
            "sub": str(user.id),
            "exp": datetime.now() + timedelta(days=settings.refresh_token_expire_days),
            "type": "refresh",
            "jti": TokenService._create_jti()
        }

        access_token = jwt.encode(access_payload, settings.secret_key, algorithm=settings.algorithm)
        refresh_token = jwt.encode(refresh_payload, settings.secret_key, algorithm=settings.algorithm)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    @staticmethod
    async def block_token(exp_refresh_token: str) -> None:
        refresh_payload = TokenService.decode_token(exp_refresh_token)
        await TokenRepository.set_record(
            jti=refresh_payload['jti'],
            ttl_seconds=refresh_payload["exp"]
        )

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=settings.algorithm)
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token has expired")
        except jwt.InvalidTokenError:
            raise TokenInvalidError("Invalid token")