# mypy: ignore-errors
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dao.base import BaseDAO
from backend.models.user import User


class UserDAO(BaseDAO[User]):
    """DAO для работы с пользователями."""

    model = User

    @classmethod
    async def get_by_telegram_id(
        cls, session: AsyncSession, telegram_id: int
    ) -> User | None:
        """Получить пользователя по Telegram ID."""
        query = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_active_users(cls, session: AsyncSession) -> list[User]:
        """Получить всех активных пользователей."""
        query = select(User).where(User.is_active)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_users_by_username(
        cls, session: AsyncSession, username: str
    ) -> list[User]:
        """Получить пользователей по username."""
        query = select(User).where(User.username == username)
        result = await session.execute(query)
        return result.scalars().all()
