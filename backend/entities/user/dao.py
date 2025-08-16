# mypy: ignore-errors

from backend.dao.base import BaseDAO
from backend.entities.user.models import User


class UserDAO(BaseDAO[User]):
    """DAO для работы с пользователями."""

    model = User
