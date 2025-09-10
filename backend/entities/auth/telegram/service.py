"""Сервис для авторизации через Telegram."""

from fastapi import HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.entities.auth.telegram.schemas import (
    TelegramAuthRequest,
    TelegramAuthResponse,
)
from backend.entities.auth.telegram.utils import (
    is_telegram_data_fresh,
    parse_telegram_init_data,
    validate_telegram_init_data,
)
from backend.entities.assemblers.schemas import SUser
from backend.entities.user.service import UserService


class TelegramAuthService:
    """Сервис для авторизации через Telegram."""

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def authenticate_telegram_user(
        self,
        auth_request: TelegramAuthRequest,
        response: Response,
        db: AsyncSession
    ) -> TelegramAuthResponse:
        """
        Аутентифицирует пользователя через Telegram.

        Args:
            auth_request: Запрос на авторизацию
            response: HTTP ответ
            db: Сессия базы данных

        Returns:
            TelegramAuthResponse: Ответ с токенами

        Raises:
            HTTPException: Если авторизация не удалась
        """
        try:
            # Валидируем данные Telegram
            if not validate_telegram_init_data(auth_request.init_data):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Невалидные данные Telegram"
                )

            # Парсим данные
            init_data = parse_telegram_init_data(auth_request.init_data)

            # Проверяем свежесть данных (не старше 24 часов)
            if not is_telegram_data_fresh(init_data.auth_date):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Данные авторизации устарели"
                )

            # Извлекаем данные пользователя
            if not init_data.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Данные пользователя не найдены"
                )

            telegram_user = init_data.user

            # Ищем или создаем пользователя
            user = await self._get_or_create_telegram_user(
                telegram_user, db
            )

            # Создаем токены
            tokens = await self.user_service.create_tokens(user, response)

            return TelegramAuthResponse(
                access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                token_type=tokens["token_type"],
                user={
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "telegram_id": user.telegram_id,
                    "is_admin": user.is_admin,
                }
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка авторизации через Telegram: {str(e)}"
            ) from e

    async def _get_or_create_telegram_user(
        self,
        telegram_user,
        db: AsyncSession
    ) -> SUser:
        """
        Находит существующего пользователя или создает нового.

        Args:
            telegram_user: Данные пользователя из Telegram
            db: Сессия базы данных

        Returns:
            SUser: Пользователь
        """
        # Ищем пользователя по telegram_id
        user = await self.user_service.get_user_by_telegram_id(
            telegram_user.id, db
        )

        if user:
            # Обновляем данные пользователя если нужно
            await self._update_user_from_telegram_data(
                user, telegram_user, db
            )
            return user

        # Создаем нового пользователя
        return await self._create_telegram_user(telegram_user, db)

    async def _update_user_from_telegram_data(
        self,
        user: SUser,
        telegram_user,
        db: AsyncSession
    ) -> None:
        """
        Обновляет данные пользователя из Telegram.

        Args:
            user: Пользователь
            telegram_user: Данные из Telegram
            db: Сессия базы данных
        """
        # Здесь можно добавить логику обновления данных пользователя
        # Например, обновление имени, username и т.д.

    async def _create_telegram_user(
        self,
        telegram_user,
        db: AsyncSession
    ) -> SUser:
        """
        Создает нового пользователя из данных Telegram.

        Args:
            telegram_user: Данные пользователя из Telegram
            db: Сессия базы данных

        Returns:
            SUser: Созданный пользователь
        """
        # Генерируем уникальный username если его нет
        username = telegram_user.username or f"tg_user_{telegram_user.id}"

        # Создаем пользователя
        user_data = {
            "username": username,
            "email": f"tg_{telegram_user.id}@telegram.local",
            "telegram_id": telegram_user.id,
            "is_admin": False,
        }

        return await self.user_service.create_user(user_data, db)
