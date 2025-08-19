from typing import Annotated, List, Optional, Type

from fastapi import Depends

from backend.core.logger import get_logger
from backend.entities.user.dao import UserDAODep
from backend.entities.user.interfaces import IUserDAO, IUserService
from backend.entities.user.schemas import User

logger = get_logger(__name__)


class UserService:
    """
    Сервисный слой для работы с пользователями.

    Implements `IUserService` interface.
    """

    def __init__(self, user_dao: IUserDAO):
        self.user_dao = user_dao

    async def get_all_users(self) -> List[User]:
        """
        Получить всех пользователей.

        Returns:
            List[User]: Список всех пользователей
        """
        users = await self.user_dao.get_all()
        logger.info("Retrieved users", extra={"count": len(users)})
        return [User.model_validate(user) for user in users]

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Получить пользователя по ID.

        Args:
            user_id (int): ID пользователя

        Returns:
            Optional[User]: Пользователь или None, если не найден
        """
        user = await self.user_dao.get_one_or_none(id=user_id)
        return User.model_validate(user) if user else None


UserService: Type[IUserService]


def get_user_service(user_dao: UserDAODep) -> IUserService:
    """Dependency для получения UserService."""
    return UserService(user_dao)


# Тип для использования в роутерах
UserServiceDep = Annotated[IUserService, Depends(get_user_service)]
