from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from backend.core.config import settings
from backend.logger import get_logger

logger = get_logger(__name__)


async def init_cache() -> None:
    """Инициализация кэша Redis"""
    try:
        redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
        logger.info("Initializing Redis cache with URL: %s", redis_url)
        redis = aioredis.from_url(redis_url, encoding="utf8", decode_responses=True)

        # Проверяем подключение к Redis
        await redis.ping()
        logger.info("Redis connection successful")

        FastAPICache.init(RedisBackend(redis), prefix="cache")
        logger.info("Redis cache initialized")

    except Exception as e:

        logger.error("Error initializing Redis cache: %s", str(e))
        raise
