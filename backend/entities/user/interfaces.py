"""Интерфейсы для пользовательских компонентов."""

from typing import Any, List, Optional, Protocol

from backend.core.base_dao import IBaseDAO
from backend.entities.user.models import User as UserModel
from backend.entities.user.schemas import User as UserSchema


class IUserDAO(IBaseDAO[UserModel]):
    """Интерфейс для DAO пользователей."""
    # Базовые методы уже определены в IBaseDAO


class IUserService(Protocol):
    """Интерфейс для сервиса пользователей."""

    async def get_all_users(self) -> List[UserSchema]:
        """Получить всех пользователей."""

    async def get_user_by(self, **filter_by) -> Optional[UserSchema]:
        """Получить пользователя по фильтру."""

    async def get_user_by_id(self, user_id: int) -> Optional[UserSchema]:
        """Получить пользователя по ID."""

    async def get_user_by_telegram_id(
        self, telegram_id: int
    ) -> Optional[UserSchema]:
        """Получить пользователя по Telegram ID."""

    async def get_user_by_email(self, email: str) -> Optional[UserSchema]:
        """Получить пользователя по email."""

    async def get_user_by_username(
        self, username: str
    ) -> Optional[UserSchema]:
        """Получить пользователя по username."""

    async def create_user(
        self, user_data: dict[str, Any]
    ) -> Optional[UserSchema]:
        """Создать нового пользователя."""

    async def update_user(
        self, user_id: int, user_data: dict[str, Any]
    ) -> Optional[UserSchema]:
        """Обновить пользователя."""

    async def delete_user(self, user_id: int) -> bool:
        """Удалить пользователя."""

    async def update_max_score(
        self, user_id: int, score: int
    ) -> Optional[UserSchema]:
        """Обновить максимальный счет пользователя."""
