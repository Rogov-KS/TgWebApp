# import aioredis
# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisBackend

from backend.core.config import settings
from backend.logger import get_logger

logger = get_logger(__name__)


def init_cache() -> None:
    """Инициализация кэша Redis"""
    redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
    logger.info("Initializing Redis cache with URL: %s", redis_url)
    # redis = aioredis.from_url(redis_url, encoding="utf8", decode_responses=True)
    # FastAPICache.init(RedisBackend(redis), prefix="cache-redis")
