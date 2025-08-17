from datetime import UTC, datetime, timedelta
import secrets
from typing import Annotated, List, Optional

from fastapi import Depends, HTTPException, Response, status

from backend.core.config import settings
from backend.core.logger import get_logger
from backend.entities.auth import utils as auth_utils
from backend.entities.refresh_token.dao import (
    RefreshTokenDAO,
    RefreshTokenDAODep
)
from backend.entities.refresh_token.models import RefreshToken
from backend.entities.user.dao import UserDAO, UserDAODep
from backend.entities.user.models import User


logger = get_logger(__name__)


class RefreshTokenService:
    """Сервисный слой для работы с refresh токенами."""

    def __init__(
        self,
        refresh_token_dao: RefreshTokenDAO,
        user_dao: UserDAO
    ):
        self.refresh_token_dao = refresh_token_dao
        self.user_dao = user_dao

    async def get_token_by_value(self, token: str) -> Optional[RefreshToken]:
        """
        Получить refresh token по значению токена.

        Args:
            token (str): Значение токена

        Returns:
            Optional[RefreshToken]: Токен или None, если не найден
        """
        logger.info("Getting refresh token by value")
        return await self.refresh_token_dao.get_by_token(token)

    async def get_active_tokens_by_user_id(
        self, user_id: int
    ) -> List[RefreshToken]:
        """
        Получить все активные refresh токены пользователя.

        Args:
            user_id (int): ID пользователя

        Returns:
            List[RefreshToken]: Список активных токенов
        """
        logger.info(
            "Getting active refresh tokens for user",
            extra={"user_id": user_id}
        )

        tokens = await self.refresh_token_dao.get_active_by_user_id(user_id)

        logger.info(
            "Retrieved active refresh tokens",
            extra={"user_id": user_id, "count": len(tokens)}
        )

        return tokens

    async def create_refresh_token(self, user_id: int) -> str:
        """
        Создать новый refresh token для пользователя с ограничением количества.

        Args:
            user_id (int): ID пользователя

        Returns:
            str: Созданный токен

        Raises:
            HTTPException: Если превышено максимальное количество токенов
        """
        logger.info(
            "Creating refresh token for user",
            extra={"user_id": user_id}
        )

        # Проверяем количество активных токенов
        active_count = await self.refresh_token_dao.count_active_by_user_id(
            user_id
        )

        max_tokens = settings.MAX_REFRESH_TOKENS_PER_USER
        if active_count >= max_tokens:
            logger.info(
                "Max refresh tokens limit reached, revoking oldest",
                extra={
                    "user_id": user_id,
                    "active_count": active_count,
                    "limit": max_tokens
                }
            )
            # Удаляем самый старый токен
            active_tokens = await self.get_active_tokens_by_user_id(user_id)
            if active_tokens:
                oldest_token = min(
                    active_tokens, key=lambda t: t.created_at
                )
                await self.revoke_token(oldest_token.token)

        # Создаем новый токен
        token_value = self._generate_token()
        expires_at = self._calculate_expiration()

        # Сохраняем в базу
        created_token = await self.refresh_token_dao.create_refresh_token(
            user_id=user_id,
            token=token_value,
            expires_at=expires_at
        )

        if not created_token:
            logger.error(
                "Failed to create refresh token",
                extra={"user_id": user_id}
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create refresh token"
            )

        logger.info(
            "Created refresh token",
            extra={"user_id": user_id, "token_id": created_token.id}
        )

        return token_value

    async def verify_refresh_token(self, token: str) -> Optional[User]:
        """
        Верифицировать refresh token и вернуть пользователя.

        Args:
            token (str): Значение токена

        Returns:
            Optional[User]: Пользователь, если токен валиден, иначе None
        """
        logger.info("Verifying refresh token")

        refresh_token = await self.get_token_by_value(token)

        if not refresh_token:
            logger.warning("Refresh token not found")
            return None

        logger.info(
            "Found refresh token",
            extra={
                "token_id": refresh_token.id,
                "user_id": refresh_token.user_id,
                "is_revoked": refresh_token.is_revoked,
                "expires_at": refresh_token.expires_at.isoformat()
            }
        )

        # Проверяем, что токен активен и не истек
        if refresh_token.is_revoked:
            logger.warning("Refresh token is revoked")
            return None

        if refresh_token.expires_at <= datetime.now(UTC):
            logger.warning("Refresh token is expired")
            return None

        # Получаем пользователя
        user = await self.user_dao.get_one_or_none(id=refresh_token.user_id)

        if not user:
            logger.warning(
                "User not found for refresh token",
                extra={"user_id": refresh_token.user_id}
            )
            return None

        logger.info(
            "Refresh token verified successfully",
            extra={"user_id": user.id}
        )

        return user

    async def revoke_token(self, token: str) -> bool:
        """
        Отозвать refresh token.

        Args:
            token (str): Значение токена

        Returns:
            bool: True, если токен был отозван, False если не найден
        """
        logger.info("Revoking refresh token")

        # Проверяем, что токен существует
        existing_token = await self.get_token_by_value(token)
        if not existing_token:
            logger.warning("Token not found for revocation")
            return False

        await self.refresh_token_dao.revoke_by_token(token)

        logger.info(
            "Refresh token revoked",
            extra={"token_id": existing_token.id, "user_id": existing_token.user_id}
        )

        return True

    async def revoke_all_user_tokens(self, user_id: int) -> int:
        """
        Отозвать все refresh токены пользователя.

        Args:
            user_id (int): ID пользователя

        Returns:
            int: Количество отозванных токенов
        """
        logger.info(
            "Revoking all refresh tokens for user",
            extra={"user_id": user_id}
        )

        # Получаем активные токены для подсчета
        active_tokens = await self.get_active_tokens_by_user_id(user_id)
        count = len(active_tokens)

        # Отзываем все токены
        await self.refresh_token_dao.revoke_all_by_user_id(user_id)

        logger.info(
            "Revoked all refresh tokens for user",
            extra={"user_id": user_id, "count": count}
        )

        return count

    async def cleanup_expired_tokens(self) -> None:
        """
        Удалить истекшие refresh токены из базы данных.
        Этот метод предназначен для периодического вызова (например, cron job).
        """
        logger.info("Starting cleanup of expired refresh tokens")

        try:
            await self.refresh_token_dao.delete_expired()
            logger.info("Completed cleanup of expired refresh tokens")
        except Exception as e:
            logger.error(
                "Error during cleanup of expired refresh tokens",
                extra={"error": str(e)},
                exc_info=True
            )
            raise

    async def get_user_token_count(self, user_id: int) -> int:
        """
        Получить количество активных токенов пользователя.

        Args:
            user_id (int): ID пользователя

        Returns:
            int: Количество активных токенов
        """
        count = await self.refresh_token_dao.count_active_by_user_id(user_id)

        logger.info(
            "Retrieved user token count",
            extra={"user_id": user_id, "count": count}
        )

        return count

    def _generate_token(self) -> str:
        """Сгенерировать случайный токен."""
        return secrets.token_urlsafe(32)

    def _calculate_expiration(self) -> datetime:
        """Вычислить время истечения токена."""
        expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
        return datetime.now(UTC) + timedelta(days=expire_days)

    def create_refresh_token_data(self, user_id: int) -> tuple[str, datetime]:
        """
        Создать данные для refresh token (без сохранения в БД).

        Args:
            user_id (int): ID пользователя

        Returns:
            tuple[str, datetime]: токен и время истечения
        """
        logger.info("create_refresh_token_data", extra={"user_id": user_id})
        token = self._generate_token()
        expire = self._calculate_expiration()
        return token, expire

    async def set_tokens_to_cookies(
        self, response: Response, user: User
    ) -> tuple[str, str]:
        """
        Создать токены и установить их в cookies.

        Args:
            response: HTTP response объект
            user: пользователь

        Returns:
            tuple[str, str]: access_token, refresh_token
        """
        # Создаем access token
        access_token = auth_utils.create_access_token(
            data={"sub": str(user.id)}
        )

        # Создаем refresh token
        refresh_token = await self.create_refresh_token(user.id)

        # Устанавливаем cookies через auth utils
        auth_utils.set_auth_cookies(response, access_token, refresh_token)

        logger.info("Access token created", extra={"access_token": access_token})
        logger.info("Refresh token created for user", extra={"user_id": user.id})

        return access_token, refresh_token


def get_refresh_token_service(
    refresh_token_dao: RefreshTokenDAODep,
    user_dao: UserDAODep
) -> RefreshTokenService:
    """Dependency для получения RefreshTokenService."""
    return RefreshTokenService(refresh_token_dao, user_dao)


# Тип для использования в роутерах
RefreshTokenServiceDep = Annotated[
    RefreshTokenService, Depends(get_refresh_token_service)
]
