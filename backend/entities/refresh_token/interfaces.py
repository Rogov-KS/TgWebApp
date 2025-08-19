"""Интерфейсы для компонентов refresh токенов."""

from datetime import datetime
from typing import List, Optional, Protocol

from backend.entities.refresh_token.models import RefreshToken
from backend.entities.user.models import User


class IRefreshTokenDAO(Protocol):
    """Интерфейс для DAO refresh токенов."""

    async def get_by_token(self, token: str) -> RefreshToken | None:
        """Получить refresh token по токену."""

    async def get_active_by_user_id(self, user_id: int) -> List[RefreshToken]:
        """Получить все активные refresh токены пользователя."""

    async def revoke_by_token(self, token: str) -> None:
        """Отозвать refresh token."""

    async def revoke_all_by_user_id(self, user_id: int) -> None:
        """Отозвать все refresh токены пользователя."""

    async def delete_expired(self) -> None:
        """Удалить истекшие refresh токены."""

    async def count_active_by_user_id(self, user_id: int) -> int:
        """Подсчитать количество активных токенов пользователя."""

    async def create_refresh_token(
        self,
        user_id: int,
        token: str,
        expires_at: datetime,
    ) -> RefreshToken | None:
        """Создать новый refresh token."""


class IRefreshTokenService(Protocol):
    """Интерфейс для сервиса refresh токенов."""

    async def get_token_by_value(self, token: str) -> Optional[RefreshToken]:
        """Получить refresh token по значению токена."""

    async def get_active_tokens_by_user_id(
        self, user_id: int
    ) -> List[RefreshToken]:
        """Получить все активные refresh токены пользователя."""

    async def create_refresh_token(self, user_id: int) -> str:
        """Создать новый refresh token для пользователя."""

    async def verify_refresh_token(self, token: str) -> Optional[User]:
        """Верифицировать refresh token и вернуть пользователя."""

    async def revoke_token(self, token: str) -> bool:
        """Отозвать refresh token."""

    async def revoke_all_user_tokens(self, user_id: int) -> int:
        """Отозвать все refresh токены пользователя."""

    async def cleanup_expired_tokens(self) -> None:
        """Удалить истекшие refresh токены из базы данных."""

    async def get_user_token_count(self, user_id: int) -> int:
        """Получить количество активных токенов пользователя."""

    def create_refresh_token_data(
        self, user_id: int
    ) -> tuple[str, datetime]:
        """Создать данные для refresh token (без сохранения в БД)."""
