import time

from fastapi import Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import Response

from backend.core.logger import get_logger

logger = get_logger(__name__)


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования времени обработки запроса
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        # Засекаем время начала обработки запроса
        start_time = time.time()

        # Обрабатываем запрос
        response = await call_next(request)

        # Вычисляем время обработки запроса
        process_time = time.time() - start_time

        # Логируем время обработки запроса
        logger.info("Request handling time", extra={"process_time": round(process_time, 4)})

        return response
