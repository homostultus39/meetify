from services.redis.connection import redis_client


class TokenRepository:
    @staticmethod
    async def set_record(jti: str, ttl_seconds: int) -> bool:
        return await redis_client.setex(
            name=f"denylist:{jti}",
            time=ttl_seconds,
            value="blocked"
        )
    
    @staticmethod
    async def exists(jti: str) -> bool:
        return await redis_client.exists(f"denylist:{jti}")