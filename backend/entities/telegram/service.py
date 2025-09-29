"""Сервис для авторизации через Telegram."""

from fastapi import HTTPException, Response, status
from fastapi import Depends
from typing import Annotated
# from backend.entities.telegram.schemas import (
# )
from backend.core.logger import get_logger
from backend.entities.telegram.utils import (
    is_telegram_data_fresh,
    parse_telegram_init_data,
    validate_telegram_init_data,
)
from backend.entities.assemblers.schemas import SUser, SUserAuthViaTelegram
from backend.entities.user.service import UserService, UserServiceDep
from backend.entities.refresh_token.service import RefreshTokenService, RefreshTokenServiceDep

from backend.entities.auth.utils import (
    create_access_token,
    set_auth_cookies,
)

logger = get_logger(__name__)


class TelegramAuthService:
    """Сервис для авторизации через Telegram."""

    def __init__(self, user_service: UserService, refresh_service: RefreshTokenService):
        self.user_service = user_service
        self.refresh_service = refresh_service

    async def authenticate_telegram_user(
        self,
        init_data: str,
        response: Response,
    ) -> dict[str, str]:
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
        logger.info(
            "Telegram auth request received",
            extra={"init_data_length": len(init_data)}
        )
        try:
            # Валидируем данные Telegram
            if not validate_telegram_init_data(init_data):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Невалидные данные Telegram"
                )
            logger.info(
                "Telegram init data validated",
                extra={"init_data": init_data}
            )
            # Парсим данные
            init_data_obj = parse_telegram_init_data(init_data)
            logger.info(
                "GET Telegram init data parsed",
                extra={"init_data": init_data_obj}
            )

            # Проверяем свежесть данных (не старше 24 часов)
            if not is_telegram_data_fresh(init_data_obj.auth_date):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Данные авторизации устарели"
                )
            logger.info(
                "success validate telegram auth date"
            )
            # Извлекаем данные пользователя
            if not init_data_obj.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Данные пользователя не найдены"
                )

            telegram_user = init_data_obj.user

            logger.info(
                "telegram_user",
                extra={"telegram_user": telegram_user}
            )

            # Ищем или создаем пользователя
            user = await self._get_or_create_telegram_user(
                telegram_user
            )

            logger.info(
                "GET User found or created",
                extra={"user": user}
            )

            # Создаем токены
            access_token = create_access_token(user.id)
            refresh_token = await self.refresh_service.create_refresh_token(
                user.id
            )
            logger.info("before setting tokens to cookies")
            set_auth_cookies(
                response=response,
                access_token=access_token,
                refresh_token=refresh_token,
            )

            logger.info(
                "Telegram auth after getted tokens",
                extra={"access_token": access_token, "refresh_token": refresh_token}
            )

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }

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
    ) -> SUser:
        """
        Находит существующего пользователя или создает нового.

        Args:
            telegram_user: Данные пользователя из Telegram
            db: Сессия базы данных

        Returns:
            SUser: Пользователь
        """
        logger.info(
            "Try to get or create telegram user",
            extra={"telegram_user": telegram_user}
        )
        # Ищем пользователя по telegram_id
        user = await self.user_service.get_user_by(
            telegram_id=telegram_user.id
        )
        logger.info(
            "User found by telegram_id",
            extra={"user": user}
        )

        if user:
            # Обновляем данные пользователя если нужно
            logger.info(
                "Try to update user from telegram data",
            )
            await self._update_user_from_telegram_data(
                user, telegram_user
            )
        else:
            logger.info(
                "Try to create user from telegram data",
            )
            user = await self._create_telegram_user(telegram_user)

        logger.info(
            "User found or created",
            extra={"user": user}
        )

        # Создаем нового пользователя
        return user

    async def _update_user_from_telegram_data(
        self,
        user: SUser,
        telegram_user,
    ) -> None:
        """
        Обновляет данные пользователя из Telegram.

        Args:
            user: Пользователь
            telegram_user: Данные из Telegram
        """
        # Здесь можно добавить логику обновления данных пользователя
        # Например, обновление имени, username и т.д.

    async def _create_telegram_user(
        self,
        telegram_user,
    ) -> SUser:
        """
        Создает нового пользователя из данных Telegram.

        Args:
            telegram_user: Данные пользователя из Telegram

        Returns:
            SUser: Созданный пользователь
        """
        # Генерируем уникальный username если его нет
        logger.info(
            "Try to create user from telegram data",
            extra={"telegram_user": telegram_user, "type": type(telegram_user)}
        )
        username = telegram_user.username or f"tg_user_{telegram_user.telegram_id}"

        # Создаем пользователя
        user_data = {
            "username": username,
            "telegram_id": telegram_user.id,
        }
        user_data = SUserAuthViaTelegram(**user_data)
        logger.info(
            "Try to create user from telegram data",
            extra={"user_data": user_data}
        )

        created_user = await self.user_service.create_user(user_data)
        logger.info(
            "User created",
            extra={"user": created_user}
        )
        return created_user


def get_telegram_auth_service(
    user_service: UserServiceDep,
    refresh_service: RefreshTokenServiceDep,
) -> TelegramAuthService:
    """Получить сервис Telegram авторизации."""
    return TelegramAuthService(user_service, refresh_service)


TelegramAuthServiceDep = Annotated[TelegramAuthService, Depends(get_telegram_auth_service)]
