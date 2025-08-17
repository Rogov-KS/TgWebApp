from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from backend.core.base_dao import BaseDAO
from backend.core.database import async_session_maker
from backend.core.logger import get_logger
from backend.entities.game_session.models import GameSession as GameSessionDB

logger = get_logger(__name__)


class GameSessionDAO(BaseDAO[GameSessionDB]):
    """DAO для работы с игровыми сессиями."""

    model = GameSessionDB

    @classmethod
    async def get_max_score(cls, user_id: int) -> int | None:
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

        async with async_session_maker() as session:
            try:
                query = select(func.max(cls.model.score)).where(
                    cls.model.user_id == user_id
                )
                result = await session.execute(query)
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
