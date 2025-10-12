"""Роутер для Telegram авторизации."""

from fastapi import APIRouter, Response
from fastapi_versioning import version

from backend.core.logger import get_logger
from backend.entities.telegram.schemas import TelegramAuthRequest
from backend.entities.telegram.service import TelegramAuthServiceDep

logger = get_logger(__name__)

router = APIRouter(
    prefix="/auth/telegram",
    tags=["Telegram Auth"],
)


@router.post("/")
@version(1)
async def telegram_auth(
    request: TelegramAuthRequest,
    response: Response,
    telegram_service: TelegramAuthServiceDep,
) -> dict[str, str]:
    """
    Авторизация через Telegram Mini App.

    Принимает initData от Telegram Mini App и выполняет авторизацию
    пользователя. Если пользователь не существует, создает нового.

    Args:
        init_data: Запрос с initData от Telegram
        response: HTTP ответ для установки cookies
        telegram_service: Сервис Telegram авторизации (dependency)

    Returns:
        TelegramAuthResponse: Ответ с токенами и данными пользователя

    Raises:
        HTTPException: 401 если данные невалидны или устарели
        HTTPException: 500 при внутренней ошибке
    """
    logger.info(
        "Telegram auth request received",
        extra={"init_data_length": len(request.init_data), "init_data": request.init_data},
    )
    try:
        result = await telegram_service.authenticate_telegram_user(request.init_data, response)
        logger.info("Telegram auth result", extra={"result": result})

        logger.info("Telegram auth successful", extra={"user_id": result.get("user_id")})

        return result

    except Exception as e:
        logger.error("Telegram auth failed", extra={"error": str(e)})
        raise
