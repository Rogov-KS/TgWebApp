# mypy: ignore-errors

from backend.dao.base import BaseDAO
from backend.models.user import User


class UserDAO(BaseDAO[User]):
    """DAO для работы с пользователями."""

    model = User
