from redis.asyncio import Redis
from management.settings import get_settings

settings = get_settings()

redis_client = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password,
    db=settings.redis_db,
    decode_responses=False
)