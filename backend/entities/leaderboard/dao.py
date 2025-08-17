from typing import Annotated

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import AsyncSessionDep
from backend.core.logger import get_logger
from backend.entities.game_session.models import GameSession
from backend.entities.leaderboard.schemas import LeaderboardPlace
from backend.entities.user.models import User

logger = get_logger(__name__)


class LeaderboardDAO:
    """DAO для работы с рейтингом игроков."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_leaderboard(
        self,
        limit: int = 10,
        offset: int = 0,
        sort_order: str = "desc",
    ) -> list[LeaderboardPlace]:
        """Получить топ игроков по максимальному количеству очков."""
        logger.info(
            "Fetching leaderboard",
            extra={"limit": limit, "offset": offset, "sort_order": sort_order}
        )

        subquery = (
            select(
                GameSession.user_id,
                func.max(GameSession.score).label("max_score")
            )
            .group_by(GameSession.user_id)
            .subquery()
        )

        query = (
            select(User, subquery.c.max_score)
            .join(subquery, User.id == subquery.c.user_id)
            .order_by(
                subquery.c.max_score.desc()
                if sort_order == "desc"
                else subquery.c.max_score.asc()
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(query)
        rows = result.fetchall()

        leaderboard = [
            LeaderboardPlace(
                user_id=user.id,
                max_score=max_score,
                place=index + offset + 1
            )
            for index, (user, max_score) in enumerate(rows)
        ]

        logger.info(
            "Fetched leaderboard",
            extra={"count": len(leaderboard)}
        )

        return leaderboard


def get_leaderboard_dao(session: AsyncSessionDep) -> LeaderboardDAO:
    """Dependency для получения LeaderboardDAO."""
    return LeaderboardDAO(session)


# Тип для использования в других модулях
LeaderboardDAODep = Annotated[LeaderboardDAO, Depends(get_leaderboard_dao)]
