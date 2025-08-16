# mypy: ignore-errors

from backend.core.base_dao import BaseDAO
from backend.entities.user.models import User


class UserDAO(BaseDAO[User]):
    """DAO для работы с пользователями."""

    model = User
