# mypy: ignore-errors
from typing import Annotated, Type

from fastapi import Depends

from backend.core.base_dao import BaseDAO
from backend.core.database import AsyncSessionDep
from backend.entities.user.models import User
from backend.entities.user.interfaces import IUserDAO


class UserDAO(BaseDAO[User]):
    """
    DAO (Data Access Object) для работы с пользователями.

    Implements `IUserDAO` interface.
    """

    model = User


UserDAO: Type[IUserDAO]


def get_user_dao(session: AsyncSessionDep) -> IUserDAO:
    """Dependency для получения UserDAO."""
    return UserDAO(session)


# Тип для использования в других модулях
UserDAODep = Annotated[IUserDAO, Depends(get_user_dao)]
