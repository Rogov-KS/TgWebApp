"""Интерфейсы для пользовательских компонентов."""

from typing import List, Optional, Protocol

from backend.core.base_dao import IBaseDAO
from backend.entities.user.models import UserDB
from backend.entities.assemblers.schemas import SUser


class IUserDAO(IBaseDAO[UserDB]):
    """Интерфейс для DAO пользователей."""
    # Базовые методы уже определены в IBaseDAO


class IUserService(Protocol):
    """Интерфейс для сервиса пользователей."""

    async def get_all_users(self) -> List[SUser]:
        """Получить всех пользователей."""

    async def get_user_by_id(self, user_id: int) -> Optional[SUser]:
        """Получить пользователя по ID."""

    async def get_user_by(self, **filter_by) -> Optional[SUser]:
        """Получить пользователя по фильтру."""
