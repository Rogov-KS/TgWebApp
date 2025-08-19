from datetime import UTC, datetime
from typing import Annotated, Type

from fastapi import Depends
from sqlalchemy import and_, select

from backend.core.base_dao import BaseDAO
from backend.core.database import async_session_maker, AsyncSessionDep
from backend.core.logger import get_logger
from backend.entities.refresh_token.interfaces import IRefreshTokenDAO
from backend.entities.refresh_token.models import RefreshToken

logger = get_logger(__name__)


class RefreshTokenDAO(BaseDAO[RefreshToken]):
    """
    DAO (Data Access Object) для работы с refresh токенами через таблицу refresh_tokens,
    которая хранит только refresh токены нашего приложения.

    Implements `IRefreshTokenDAO` interface.
    """

    model = RefreshToken

    async def get_by_token(self, token: str) -> RefreshToken | None:
        """Получить refresh token по токену."""
        return await self.get_one_or_none(token=token)

    async def get_active_by_user_id(self, user_id: int) -> list[RefreshToken]:
        """Получить все активные refresh токены пользователя."""
        stmt = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.is_revoked == False,  # noqa: E712
                self.model.expires_at > datetime.now(UTC),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def revoke_by_token(self, token: str) -> None:
        """Отозвать refresh token."""
        await self.update({"token": token}, {"is_revoked": True})

    async def revoke_all_by_user_id(self, user_id: int) -> None:
        """Отозвать все refresh токены пользователя."""
        active_tokens = await self.get_active_by_user_id(user_id)
        for token in active_tokens:
            await self.update({"id": token.id}, {"is_revoked": True})

    async def delete_expired(self) -> None:
        """Удалить истекшие refresh токены."""
        stmt = select(self.model).where(
            self.model.expires_at <= datetime.now(UTC)
        )
        result = await self.session.execute(stmt)
        expired_tokens = result.scalars().all()

        for token in expired_tokens:
            await self.session.delete(token)
        await self.session.commit()

    async def count_active_by_user_id(self, user_id: int) -> int:
        """Подсчитать количество активных токенов пользователя."""
        active_tokens = await self.get_active_by_user_id(user_id)
        return len(active_tokens)

    async def create_refresh_token(
        self,
        user_id: int,
        token: str,
        expires_at: datetime,
    ) -> RefreshToken | None:
        """Создать новый refresh token."""
        return await self.create(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            is_revoked=False
        )


RefreshTokenDAO: Type[IRefreshTokenDAO]


def get_refresh_token_dao(session: AsyncSessionDep) -> IRefreshTokenDAO:
    """Dependency для получения RefreshTokenDAO."""
    return RefreshTokenDAO(session)


# Тип для использования в других модулях
RefreshTokenDAODep = Annotated[IRefreshTokenDAO, Depends(get_refresh_token_dao)]
