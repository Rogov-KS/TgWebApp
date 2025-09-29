from typing import Annotated, List, Optional

from fastapi import Depends

from backend.core.logger import get_logger
from backend.entities.user.dao import UserDAODep, UserDAO
from backend.entities.assemblers.schemas import SUser, SUserAuth

logger = get_logger(__name__)


class UserService:
    """
    Сервисный слой для работы с пользователями.
    """

    def __init__(self, user_dao: UserDAO):
        self.user_dao = user_dao

    async def get_all_users(self) -> List[SUser]:
        """
        Получить всех пользователей.

        Returns:
            List[SUser]: Список всех пользователей
        """
        users = await self.user_dao.get_all()
        logger.info("Retrieved users", extra={"count": len(users)})
        return [SUser.model_validate(user) for user in users]

    async def get_user_by_id(self, user_id: int) -> Optional[SUser]:
        """
        Получить пользователя по ID.

        Args:
            user_id (int): ID пользователя

        Returns:
            Optional[SUser]: Пользователь или None, если не найден
        """
        user = await self.user_dao.get_one_or_none(id=user_id)
        return SUser.model_validate(user) if user else None

    async def get_user_by(self, **filter_by) -> Optional[SUser]:
        """
        Получить пользователя по фильтру.

        Args:
            **filter_by: Фильтр

        Returns:
            Optional[SUser]: Пользователь или None, если не найден
        """
        user = await self.user_dao.get_one_or_none(**filter_by)
        return SUser.model_validate(user) if user else None

    async def create_user(self, user_data: SUserAuth) -> SUser:
        """
        Создать пользователя.
        """
        logger.info(
            "Try to create user",
            extra={"user_data": user_data}
        )
        user = await self.user_dao.create(
            username=user_data.username,
            hashed_password=None,
            telegram_id=user_data.telegram_id,
        )
        logger.info(
            "User created",
            extra={"user": user}
        )
        return SUser.model_validate(user)

def get_user_service(user_dao: UserDAODep) -> UserService:
    """Dependency для получения UserService."""
    return UserService(user_dao)


# Тип для использования в роутерах
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
