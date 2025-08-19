from typing import Annotated, Type

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from backend.core.base_dao import BaseDAO
from backend.core.database import AsyncSessionDep
from backend.core.logger import get_logger
from backend.entities.game_session.interfaces import IGameSessionDAO
from backend.entities.game_session.models import GameSession as GameSessionDB

logger = get_logger(__name__)


class GameSessionDAO(BaseDAO[GameSessionDB]):
    """
    DAO (Data Access Object) для работы с игровыми сессиями.

    Implements `IGameSessionDAO` interface.
    """

    model = GameSessionDB

    async def get_max_score(self, user_id: int) -> int | None:
        """
        Получить максимальный счет пользователя.

        Args:
            user_id: ID пользователя

        Returns:
            Максимальный счет (int) или None, если у пользователя нет записей

        Raises:
            ValueError: Если user_id не является положительным числом
        """
        if not isinstance(user_id, int) or user_id <= 0:
            msg = "user_id должен быть положительным целым числом"
            logger.exception(msg, extra={"user_id": user_id}, exc_info=True)
            raise ValueError(msg)

        try:
            query = select(func.max(self.model.score)).where(
                self.model.user_id == user_id
            )
            result = await self.session.execute(query)
            max_score = result.scalar_one_or_none()
            return int(max_score) if max_score is not None else None
        except SQLAlchemyError as e:
            logger.exception(
                "Ошибка при получении максимального счета",
                extra={"user_id": user_id},
                exc_info=True,
            )
            msg = "Ошибка при получении максимального счета"
            raise ValueError(msg) from e


GameSessionDAO: Type[IGameSessionDAO]


def get_game_session_dao(session: AsyncSessionDep) -> IGameSessionDAO:
    """Dependency для получения GameSessionDAO."""
    return GameSessionDAO(session)


# Тип для использования в других модулях
GameSessionDAODep = Annotated[IGameSessionDAO, Depends(get_game_session_dao)]
