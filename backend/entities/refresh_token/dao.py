from datetime import UTC, datetime

from sqlalchemy import and_, select

from backend.core.base_dao import BaseDAO
from backend.core.database import async_session_maker
from backend.entities.refresh_token.models import RefreshToken


class RefreshTokenDAO(BaseDAO[RefreshToken]):
    """DAO для работы с refresh токенами через таблицу refresh_tokens,
    которая хранит только refresh токены нашего приложения."""

    model = RefreshToken

    @classmethod
    async def get_by_token(cls, token: str) -> RefreshToken | None:
        """Получить refresh token по токену."""
        return await cls.get_one_or_none(token=token)

    @classmethod
    async def get_active_by_user_id(cls, user_id: int) -> list[RefreshToken]:
        """Получить все активные refresh токены пользователя."""
        async with async_session_maker() as session:
            stmt = select(cls.model).where(
                and_(
                    cls.model.user_id == user_id,
                    cls.model.is_revoked == False,  # noqa: E712
                    cls.model.expires_at > datetime.now(UTC),
                )
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    @classmethod
    async def revoke_by_token(cls, token: str) -> None:
        """Отозвать refresh token."""
        await cls.update({"token": token}, {"is_revoked": True})

    @classmethod
    async def revoke_all_by_user_id(cls, user_id: int) -> None:
        """Отозвать все refresh токены пользователя."""
        active_tokens = await cls.get_active_by_user_id(user_id)
        for token in active_tokens:
            await cls.update({"id": token.id}, {"is_revoked": True})

    @classmethod
    async def delete_expired(cls) -> None:
        """Удалить истекшие refresh токены."""
        async with async_session_maker() as session:
            stmt = select(cls.model).where(cls.model.expires_at <= datetime.now(UTC))
            result = await session.execute(stmt)
            expired_tokens = result.scalars().all()

            for token in expired_tokens:
                await session.delete(token)
            await session.commit()

    @classmethod
    async def count_active_by_user_id(cls, user_id: int) -> int:
        """Подсчитать количество активных токенов пользователя."""
        active_tokens = await cls.get_active_by_user_id(user_id)
        return len(active_tokens)

    @classmethod
    async def create_refresh_token(
        cls,
        user_id: int,
        token: str,
        expires_at: datetime,
    ) -> RefreshToken | None:
        """Создать новый refresh token."""
        return await cls.create(
            user_id=user_id, token=token, expires_at=expires_at, is_revoked=False
        )
