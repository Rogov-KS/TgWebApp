import sys
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.endpoints import auth, game_sessions, leaderboard, test
from backend.core.config import settings
from backend.logger import get_logger, setup_logging
from backend.oauth2 import router as oauth2_router
from backend.oauth2.cleanup import start_cleanup_task

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
app.include_router(test.router)
app.include_router(oauth2_router)
app.include_router(auth.router)
# app.include_router(users.router) # noqa
app.include_router(game_sessions.router)
app.include_router(leaderboard.router)

logger = get_logger(__name__)


@app.on_event("startup")
async def startup_event() -> None:
    """Событие при запуске приложения"""
    logger.info("Starting OAuth cleanup task...")
    start_cleanup_task()


if __name__ == "__main__":
    setup_logging()
    # logger.info("sys.path: %s", sys.path)
    # logger.info("settings config[CORS]: %s", json.dumps(settings.get_cors_attrs(), indent=4))
    # logger.info("settings config[SMTP]: %s", json.dumps(settings.get_smtp_attrs(), indent=4))

    logger.info("Starting the application...")
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
    logger.info("Application ended")
