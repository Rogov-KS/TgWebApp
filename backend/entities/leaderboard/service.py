from typing import Annotated, List

from fastapi import Depends

from backend.core.logger import get_logger
from backend.entities.game_session.dao import GameSessionDAODep, GameSessionDAO
from backend.entities.leaderboard.dao import LeaderboardDAODep, LeaderboardDAO
from backend.entities.assemblers.schemas import SLeaderboardPlace
from backend.entities.assemblers.schemas import SUser

logger = get_logger(__name__)


class LeaderboardService:
    """
    Сервисный слой для работы с рейтингом игроков.
    """

    def __init__(
        self,
        leaderboard_dao: LeaderboardDAO,
        game_session_dao: GameSessionDAO
    ):
        self.leaderboard_dao = leaderboard_dao
        self.game_session_dao = game_session_dao

    async def get_leaderboard(
        self,
        limit: int = 10,
        offset: int = 0,
        sort_order: str = "desc",
    ) -> List[SLeaderboardPlace]:
        """
        Получить рейтинг игроков.

        Args:
            limit (int): Максимальное количество записей
            offset (int): Смещение для пагинации
            sort_order (str): Порядок сортировки ("desc" или "asc")

        Returns:
            List[LeaderboardPlace]: Список мест в рейтинге
        """
        logger.info(
            "Getting leaderboard",
            extra={
                "limit": limit,
                "offset": offset,
                "sort_order": sort_order
            }
        )

        # Валидация параметров
        if limit <= 0:
            limit = 10
        if limit > 100:  # Ограничиваем максимальное количество записей
            limit = 100
        if offset < 0:
            offset = 0
        if sort_order not in ["desc", "asc"]:
            sort_order = "desc"

        leaderboard = await self.leaderboard_dao.get_leaderboard(
            limit=limit,
            offset=offset,
            sort_order=sort_order
        )

        logger.info(
            "Retrieved leaderboard",
            extra={"count": len(leaderboard)}
        )

        return leaderboard

    async def get_user_max_score(self, user: SUser) -> int | None:
        """
        Получить максимальный счет пользователя.

        Args:
            user (User): Пользователь

        Returns:
            int | None: Максимальный счет или None, если игр не было
        """
        logger.info(
            "Getting user max score",
            extra={"user_id": user.id}
        )

        max_score = await self.game_session_dao.get_max_score(user.id)

        logger.info(
            "Retrieved user max score",
            extra={"user_id": user.id, "max_score": max_score}
        )

        return max_score

    async def get_user_position_in_leaderboard(self, user: SUser) -> int | None:
        """
        Получить позицию пользователя в общем рейтинге.

        Args:
            user (User): Пользователь

        Returns:
            int | None: Позиция в рейтинге или None, если не в рейтинге
        """
        logger.info(
            "Getting user position in leaderboard",
            extra={"user_id": user.id}
        )

        # Получаем максимальный счет пользователя
        user_max_score = await self.get_user_max_score(user)

        if user_max_score is None:
            logger.info(
                "User has no games played",
                extra={"user_id": user.id}
            )
            return None

        # Получаем полный рейтинг до нахождения пользователя
        # Это можно оптимизировать с помощью COUNT запроса в будущем
        position = None
        offset = 0
        limit = 50

        while position is None:
            chunk = await self.leaderboard_dao.get_leaderboard(
                limit=limit,
                offset=offset,
                sort_order="desc"
            )

            if not chunk:
                # Больше нет записей в рейтинге
                break

            for entry in chunk:
                if entry.user_id == user.id:
                    position = entry.place
                    break

            offset += limit

            # Ограничиваем поиск разумными пределами
            if offset > 1000:
                break

        logger.info(
            "Retrieved user position in leaderboard",
            extra={"user_id": user.id, "position": position}
        )

        return position


def get_leaderboard_service(
    leaderboard_dao: LeaderboardDAODep,
    game_session_dao: GameSessionDAODep
) -> LeaderboardService:
    """Dependency для получения LeaderboardService."""
    return LeaderboardService(leaderboard_dao, game_session_dao)


# Тип для использования в роутерах
LeaderboardServiceDep = Annotated[LeaderboardService, Depends(get_leaderboard_service)]
