from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import settings
from backend.core.database import async_session_maker
from backend.core.dependecies import get_current_user
from backend.dao.user import UserDAO
from backend.models.user import User
from backend.schemas.telegram import (
    TelegramAuthRequest,
    TelegramAuthResponse,
    TelegramUserData,
    TelegramValidationResponse,
)
from backend.utils.auth import create_access_token
from backend.utils.telegram import validate_telegram_init_data

router = APIRouter(prefix="/telegram", tags=["telegram"])


async def get_async_session() -> AsyncSession:
    """Получение асинхронной сессии базы данных."""
    async with async_session_maker() as session:
        yield session


@router.post("/auth", response_model=TelegramAuthResponse)
async def telegram_auth(
    auth_request: TelegramAuthRequest,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> TelegramAuthResponse:
    """
    Авторизация через Telegram Web App.

    Args:
        auth_request: Запрос с initData от Telegram
        response: Объект ответа для установки cookies
        session: Сессия базы данных

    Returns:
        JWT токен и данные пользователя

    Raises:
        HTTPException: При ошибке валидации или авторизации
    """
    try:
        # Валидация initData
        validated_data = validate_telegram_init_data(auth_request.init_data)
        user_data = validated_data["user"]

        # Создание или обновление пользователя
        user_dao = UserDAO()

        # Проверяем существование пользователя
        existing_user = await user_dao.get_by_telegram_id(user_data["id"])

        if existing_user:
            # Обновляем данные пользователя
            update_data = {
                "first_name": user_data["first_name"],
                "last_name": user_data.get("last_name"),
                "username": user_data.get("username"),
                "language_code": user_data.get("language_code"),
                "is_premium": user_data.get("is_premium", False),
                "photo_url": user_data.get("photo_url"),
                "telegram_username": user_data.get("username"),
            }
            user = await user_dao.update(
                filters={"id": existing_user.id}, update_data=update_data
            )
        else:
            # Создаем нового пользователя
            user = await user_dao.create(
                telegram_id=user_data["id"],
                first_name=user_data["first_name"],
                last_name=user_data.get("last_name"),
                username=user_data.get("username"),
                language_code=user_data.get("language_code"),
                is_premium=user_data.get("is_premium", False),
                photo_url=user_data.get("photo_url"),
                telegram_username=user_data.get("username"),
                hashed_password="",  # Для Telegram авторизации пароль не нужен
            )

        # Создание JWT токена
        access_token = create_access_token(data={"sub": str(user.id)})

        # Устанавливаем токен в cookies
        response.set_cookie(
            settings.ACCESS_TOKEN_COOKIE_NAME,
            access_token,
            httponly=True,
            secure=True,  # Для HTTPS
            samesite="strict",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        # Формирование ответа
        telegram_user = TelegramUserData(
            id=user.telegram_id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            language_code=user.language_code,
            is_premium=user.is_premium,
            photo_url=user.photo_url,
        )

        return TelegramAuthResponse(
            access_token=access_token,
            token_type="bearer",
            user=telegram_user,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Telegram authentication failed: {e!s}",
        )


@router.post("/validate", response_model=TelegramValidationResponse)
async def validate_telegram_data(
    auth_request: TelegramAuthRequest,
) -> TelegramValidationResponse:
    """
    Валидация данных от Telegram.

    Args:
        auth_request: Запрос с initData от Telegram

    Returns:
        Результат валидации и данные пользователя
    """
    try:
        # Валидация initData
        validated_data = validate_telegram_init_data(auth_request.init_data)
        user_data = validated_data["user"]

        # Формирование ответа
        telegram_user = TelegramUserData(
            id=user_data["id"],
            first_name=user_data["first_name"],
            last_name=user_data.get("last_name"),
            username=user_data.get("username"),
            language_code=user_data.get("language_code"),
            is_premium=user_data.get("is_premium", False),
            photo_url=user_data.get("photo_url"),
        )

        return TelegramValidationResponse(
            is_valid=True,
            user_data=telegram_user,
        )

    except Exception as e:
        return TelegramValidationResponse(
            is_valid=False,
            error_message=str(e),
        )


@router.get("/user", response_model=TelegramUserData)
async def get_telegram_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> TelegramUserData:
    """
    Получение данных пользователя из Telegram.

    Args:
        current_user: Текущий авторизованный пользователь

    Returns:
        Данные пользователя Telegram
    """
    return TelegramUserData(
        id=current_user.telegram_id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        username=current_user.username,
        language_code=current_user.language_code,
        is_premium=current_user.is_premium,
        photo_url=current_user.photo_url,
    )
