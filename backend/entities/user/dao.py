# mypy: ignore-errors
from typing import Annotated

from fastapi import Depends

from backend.core.base_dao import BaseDAO
from backend.core.database import AsyncSessionDep
from backend.entities.user.models import User


class UserDAO(BaseDAO[User]):
    """DAO для работы с пользователями."""

    model = User


def get_user_dao(session: AsyncSessionDep) -> UserDAO:
    """Dependency для получения UserDAO."""
    return UserDAO(session)


# Тип для использования в других модулях
UserDAODep = Annotated[UserDAO, Depends(get_user_dao)]
