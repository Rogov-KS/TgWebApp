import sys

from fastapi import FastAPI

from backend.api.endpoints import auth, users, game_sessions
from backend.logger import get_logger, setup_logging

# Создаем экземпляр FastAPI
app = FastAPI(title="TgWebApp API", version="1.0.0")

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(game_sessions.router)

logger = get_logger(__name__)

if __name__ == "__main__":
    setup_logging()
    logger.info("sys.path: %s", sys.path)

    logger.info("Starting the application...")
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
    logger.info("Application ended")
