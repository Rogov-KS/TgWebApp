import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.endpoints import auth, game_sessions, leaderboard
from backend.core.config import settings
from backend.logger import get_logger, setup_logging

# Создаем экземпляр FastAPI
app = FastAPI(title="TgWebApp API", version="1.0.0")

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Подключаем роутеры
app.include_router(auth.router)
# app.include_router(users.router) # noqa
app.include_router(game_sessions.router)
app.include_router(leaderboard.router)

logger = get_logger(__name__)

if __name__ == "__main__":
    setup_logging()
    logger.info("sys.path: %s", sys.path)

    logger.info("Starting the application...")
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
    logger.info("Application ended")
