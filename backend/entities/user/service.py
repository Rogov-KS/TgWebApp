from typing import Annotated, List, Optional

from fastapi import Depends

from backend.core.logger import get_logger
from backend.entities.user.dao import UserDAODep, UserDAO
from backend.entities.user.schemas import User

logger = get_logger(__name__)


class UserService:
    """Сервисный слой для работы с пользователями."""

    def __init__(self, user_dao: UserDAO):
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

    async def get_user_by_telegram_id(
        self, telegram_id: int
    ) -> Optional[User]:
        """
        Получить пользователя по Telegram ID.

        Args:
            telegram_id (int): Telegram ID пользователя

        Returns:
            Optional[User]: Пользователь или None, если не найден
        """
        user = await self.user_dao.get_one_or_none(telegram_id=telegram_id)
        return User.model_validate(user) if user else None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Получить пользователя по email.

        Args:
            email (str): Email пользователя

        Returns:
            Optional[User]: Пользователь или None, если не найден
        """
        user = await self.user_dao.get_one_or_none(email=email)
        return User.model_validate(user) if user else None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Получить пользователя по username.

        Args:
            username (str): Username пользователя

        Returns:
            Optional[User]: Пользователь или None, если не найден
        """
        user = await self.user_dao.get_one_or_none(username=username)
        return User.model_validate(user) if user else None

    async def create_user(self, user_data: dict) -> Optional[User]:
        """
        Создать нового пользователя.

        Args:
            user_data (dict): Данные пользователя

        Returns:
            Optional[User]: Созданный пользователь или None при ошибке
        """
        user = await self.user_dao.create(**user_data)
        if user:
            logger.info("Created new user", extra={"user_id": user.id})
            return User.model_validate(user)
        return None

    async def update_user(
        self, user_id: int, user_data: dict
    ) -> Optional[User]:
        """
        Обновить пользователя.

        Args:
            user_id (int): ID пользователя
            user_data (dict): Данные для обновления

        Returns:
            Optional[User]: Обновленный пользователь или None, если не найден
        """
        user = await self.user_dao.update({"id": user_id}, user_data)
        if user:
            logger.info("Updated user", extra={"user_id": user_id})
            return User.model_validate(user)
        return None

    async def delete_user(self, user_id: int) -> bool:
        """
        Удалить пользователя.

        Args:
            user_id (int): ID пользователя

        Returns:
            bool: True если пользователь удален, False если не найден
        """
        deleted = await self.user_dao.delete(id=user_id)
        if deleted:
            logger.info("Deleted user", extra={"user_id": user_id})
        return deleted

    async def update_max_score(
        self, user_id: int, score: int
    ) -> Optional[User]:
        """
        Обновить максимальный счет пользователя.

        Args:
            user_id (int): ID пользователя
            score (int): Новый счет

        Returns:
            Optional[User]: Обновленный пользователь или None, если не найден
        """
        user = await self.user_dao.get_one_or_none(id=user_id)
        if user and score > user.max_score:
            updated_user = await self.user_dao.update(
                {"id": user_id}, {"max_score": score}
            )
            if updated_user:
                logger.info(
                    "Updated user max score",
                    extra={"user_id": user_id, "new_score": score}
                )
                return User.model_validate(updated_user)
        return User.model_validate(user) if user else None


def get_user_service(user_dao: UserDAODep) -> UserService:
    """Dependency для получения UserService."""
    return UserService(user_dao)


# Тип для использования в роутерах
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
