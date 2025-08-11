import sys
import json
from contextlib import asynccontextmanager
from typing import AsyncIterator
import asyncio
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from backend.api.endpoints import auth, game_sessions, leaderboard, test
from backend.core.config import settings
from backend.logger import get_logger, setup_logging
from backend.oauth2 import router as oauth2_router
from backend.oauth2.cleanup import start_cleanup_task
from backend.cache_redis.main import init_cache


logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """События при запуске и завершении работы приложения"""
    # Событие при запуске приложения
    logger.info("Starting OAuth cleanup task...")
    start_cleanup_task()
    await init_cache()

    yield

    # Событие при завершении работы приложения
    logger.info("Stopping OAuth cleanup task...")


# Создаем экземпляр FastAPI
app = FastAPI(title="TgWebApp API", version="1.0.0", lifespan=lifespan)

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Подключаем роутеры
app.include_router(test.router)
app.include_router(oauth2_router)
app.include_router(auth.router)
# app.include_router(users.router) # noqa
app.include_router(game_sessions.router)
app.include_router(leaderboard.router)


if __name__ == "__main__":
    setup_logging()
    # logger.info("sys.path: %s", sys.path)
    # logger.info("settings config[CORS]: %s", json.dumps(settings.get_cors_attrs(), indent=4))
    # logger.info("settings config[SMTP]: %s", json.dumps(settings.get_smtp_attrs(), indent=4))

    logger.info("Starting the application...")
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
    logger.info("Application ended")
