from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from backend.core.config import settings
from backend.core.logger import get_logger

logger = get_logger(__name__)


async def init_cache() -> None:
    """Инициализация кэша Redis"""
    try:
        redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
        logger.info("Initializing Redis cache", extra={"redis_url": redis_url})
        redis = aioredis.from_url(redis_url, encoding="utf8", decode_responses=True)

        # Проверяем подключение к Redis
        await redis.ping()
        logger.info("Redis connection successful")

        FastAPICache.init(RedisBackend(redis), prefix="cache")
        logger.info("Redis cache initialized")

    except Exception:
        logger.exception("Error initializing Redis cache", exc_info=True)
        raise
