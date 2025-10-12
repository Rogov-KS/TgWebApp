from typing import Annotated, Any

from fastapi import Depends

from backend.core.logger import get_logger
from backend.entities.assemblers.schemas import SUser, SUserAuth, SUserRegister
from backend.entities.user.dao import UserDAO, UserDAODep

logger = get_logger(__name__)


class UserService:
    """
    Сервисный слой для работы с пользователями.
    """

    def __init__(self, user_dao: UserDAO):
        self.user_dao = user_dao

    async def get_all_users(self) -> list[SUser]:
        """
        Получить всех пользователей.

        Returns:
            List[SUser]: Список всех пользователей
        """
        users = await self.user_dao.get_all()
        logger.info("Retrieved users", extra={"count": len(users)})
        return [SUser.model_validate(user) for user in users]

    async def get_user_by(self, **filter_by: Any) -> SUser | None:
        """
        Получить пользователя по фильтру.

        Args:
            **filter_by: Фильтр

        Returns:
            SUser | None: Пользователь или None, если не найден
        """
        user = await self.user_dao.get_one_or_none(**filter_by)
        return SUser.model_validate(user) if user else None

    async def get_user_by_id(self, user_id: int) -> SUser | None:
        """
        Получить пользователя по ID.

        Args:
            user_id (int): ID пользователя

        Returns:
            SUser | None: Пользователь или None, если не найден
        """
        return await self.get_user_by(id=user_id)

    async def create_user(self, user_data: SUserRegister) -> SUser:
        """
        Создать пользователя.
        """
        logger.info("Try to create user", extra={"user_data": user_data})
        user = await self.user_dao.create(
            username=user_data.username,
            email=user_data.email,
            hashed_password=user_data.hashed_password,
        )
        logger.info("User created", extra={"user": user})
        return SUser.model_validate(user)

    async def create_telegram_user(self, user_data: SUserAuth) -> SUser:
        """
        Создать пользователя.
        """
        logger.info("Try to create telegram user", extra={"user_data": user_data})
        user = await self.user_dao.create(
            username=user_data.username,
            # hashed_password=user_data.hashed_password,
            telegram_id=user_data.telegram_id,
        )
        logger.info("User created", extra={"user": user})
        return SUser.model_validate(user)

    async def update_user(self, filter_by: dict[str, Any], update_data: dict[str, Any]) -> SUser:
        """
        Обновить пользователя.
        """
        user = await self.user_dao.update(filters=filter_by, update_data=update_data)
        logger.info("User updated", extra={"user": user})
        return SUser.model_validate(user)


def get_user_service(user_dao: UserDAODep) -> UserService:
    """Dependency для получения UserService."""
    return UserService(user_dao)


# Тип для использования в роутерах
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
