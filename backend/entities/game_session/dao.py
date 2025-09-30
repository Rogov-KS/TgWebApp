from typing import Annotated, Any
from collections.abc import Sequence

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from backend.core.base_dao import BaseDAO
from backend.core.database import AsyncSessionDep
from backend.core.logger import get_logger
from backend.entities.game_session.models import GameSessionDB

logger = get_logger(__name__)


class GameSessionDAO(BaseDAO[GameSessionDB]):
    """
    DAO (Data Access Object) для работы с игровыми сессиями.
    """

    model = GameSessionDB

    async def get_user_max_score(self, user_id: int) -> int | None:
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
            query = select(func.max(self.model.score)).where(self.model.user_id == user_id)
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

    async def get_leaderboard(self,
                              limit: int = 10,
                              offset: int = 0,
                              sort_order: str = "desc",
                              **filter_by: Any) -> Sequence[tuple[int, int]]:
        """
        Получить лидеров.
        """
        query = (
            select(
                self.model.user_id,
                func.max(self.model.score).label('score'),
            )
            .filter_by(**filter_by)
            .group_by(self.model.user_id)
            .order_by(
                func.max(self.model.score).desc() if sort_order == "desc"
                else func.max(self.model.score).asc()
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(query)
        return result.mappings().all()

    async def get_user_position_in_leaderboard(self, user_id: int) -> int | None:
        """
        Получить позицию пользователя в рейтинге.
        """
        # агрегируем: лучший результат по каждому пользователю
        subq = (
            select(
                self.model.user_id,
                func.max(self.model.score).label("max_score"),
            )
            .group_by(self.model.user_id)
            .subquery()
        )

        # ранжируем агрегаты по убыванию max_score
        ranked = (
            select(
                subq.c.user_id,
                func.dense_rank().over(order_by=subq.c.max_score.desc()).label("place"),
            )
            .subquery()
        )

        # выбираем место конкретного пользователя
        query = select(ranked.c.place).where(ranked.c.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


def get_game_session_dao(session: AsyncSessionDep) -> GameSessionDAO:
    """Dependency для получения GameSessionDAO."""
    return GameSessionDAO(session)


# Тип для использования в других модулях
GameSessionDAODep = Annotated[GameSessionDAO, Depends(get_game_session_dao)]
