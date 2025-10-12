import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.core.logger import get_logger
from backend.middlewares.process_time import ProcessTimeMiddleware

logger = get_logger(__name__)


def add_middlewares(app: FastAPI) -> None:
    """Добавляет middlewares в приложение"""
    # Добавляем middleware для логирования времени обработки запроса
    app.add_middleware(ProcessTimeMiddleware)

    # Настраиваем CORS
    logger.debug("settings config[CORS]:\n%s", json.dumps(settings.get_cors_attrs(), indent=4))
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )


__all__ = ["add_middlewares"]
