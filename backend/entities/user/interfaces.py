"""Интерфейсы для пользовательских компонентов."""

from typing import List, Optional, Protocol

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

    async def get_user_by_id(self, user_id: int) -> Optional[UserSchema]:
        """Получить пользователя по ID."""
