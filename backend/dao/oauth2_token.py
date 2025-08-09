from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dao.base import BaseDAO
from backend.models.oauth2_token import OAuth2Token
from backend.core.database import async_session_maker


class Oauth2TokenDAO(BaseDAO[OAuth2Token]):
    """DAO для работы с refresh токенами через таблицу oauth2_tokens."""

    model = OAuth2Token

    @classmethod
    async def get_by_token(cls, token: str) -> OAuth2Token | None:
        """Получить refresh token по токену."""
        return await cls.get_one_or_none(refresh_token=token)

    @classmethod
    async def get_active_by_user_id(cls, user_id: int) -> list[OAuth2Token]:
        """Получить все активные refresh токены пользователя."""
        async with async_session_maker() as session:
            stmt = select(cls.model).where(
                and_(
                    cls.model.user_id == user_id,
                    cls.model.is_active == True,  # noqa: E712
                    cls.model.refresh_token.isnot(None),
                    cls.model.expires_at > datetime.utcnow(),
                )
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    @classmethod
    async def revoke_by_token(cls, token: str) -> None:
        """Отозвать refresh token."""
        await cls.update({"refresh_token": token}, {"is_active": False})

    @classmethod
    async def revoke_all_by_user_id(cls, user_id: int) -> None:
        """Отозвать все refresh токены пользователя."""
        active_tokens = await cls.get_active_by_user_id(user_id)
        for token in active_tokens:
            await cls.update({"id": token.id}, {"is_active": False})

    @classmethod
    async def delete_expired(cls) -> None:
        """Удалить истекшие refresh токены."""
        async with async_session_maker() as session:
            stmt = select(cls.model).where(
                and_(
                    cls.model.expires_at <= datetime.utcnow(),
                    cls.model.refresh_token.isnot(None)
                )
            )
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
        refresh_token: str,
        expires_at: datetime,
        provider_name: str = "internal"
    ) -> OAuth2Token | None:
        """Создать новый refresh token."""
        return await cls.create(
            user_id=user_id,
            refresh_token=refresh_token,
            expires_at=expires_at,
            provider_name=provider_name,
            access_token="",  # Пустая строка для refresh токенов
            is_active=True
        )
