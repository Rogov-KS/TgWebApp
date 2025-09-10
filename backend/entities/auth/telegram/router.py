"""Роутер для Telegram авторизации."""

from fastapi import APIRouter, Depends, Response
from fastapi_versioning import version
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.logger import get_logger
from backend.entities.auth.telegram.schemas import (
    TelegramAuthRequest,
    TelegramAuthResponse,
)
from backend.entities.auth.telegram.service import TelegramAuthService
from backend.entities.user.service import UserServiceDep

logger = get_logger(__name__)

router = APIRouter(
    prefix="/auth/telegram",
    tags=["Telegram Auth"],
)


def get_telegram_auth_service(
    user_service: UserServiceDep
) -> TelegramAuthService:
    """Получить сервис Telegram авторизации."""
    return TelegramAuthService(user_service)


@router.post("/", response_model=TelegramAuthResponse)
@version(1)
async def telegram_auth(
    auth_request: TelegramAuthRequest,
    response: Response,
    telegram_service: TelegramAuthService = Depends(
        get_telegram_auth_service
    )
) -> TelegramAuthResponse:
    """
    Авторизация через Telegram Mini App.

    Принимает initData от Telegram Mini App и выполняет авторизацию
    пользователя. Если пользователь не существует, создает нового.

    Args:
        auth_request: Запрос с initData от Telegram
        response: HTTP ответ для установки cookies
        telegram_service: Сервис Telegram авторизации
        user_service: Сервис пользователей

    Returns:
        TelegramAuthResponse: Ответ с токенами и данными пользователя

    Raises:
        HTTPException: 401 если данные невалидны или устарели
        HTTPException: 500 при внутренней ошибке
    """
    logger.info(
        "Telegram auth request received",
        extra={"init_data_length": len(auth_request.init_data)}
    )

    try:
        result = await telegram_service.authenticate_telegram_user(
            auth_request, response, user_service
        )

        logger.info(
            "Telegram auth successful",
            extra={"user_id": result.user.get("id")}
        )

        return result

    except Exception as e:
        logger.error(
            "Telegram auth failed",
            extra={"error": str(e)}
        )
        raise
