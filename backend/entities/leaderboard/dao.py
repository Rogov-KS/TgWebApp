from sqlalchemy import func, select

from backend.core.database import async_session_maker
from backend.entities.game_session.models import GameSession
from backend.entities.user.models import User
from backend.entities.leaderboard.schemas import LeaderboardPlace


async def get_db_leaderboard(
    limit: int = 10,
    offset: int = 0,
    sort_order: str = "desc",
) -> list[LeaderboardPlace]:
    """Получить топ игроков по вычисленному максимальному количеству очков."""
    async with async_session_maker() as session:
        subquery = (
            select(GameSession.user_id, func.max(GameSession.score).label("max_score"))
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

        result = await session.execute(query)
        rows = result.fetchall()

        return [
            LeaderboardPlace(user_id=user.id, max_score=max_score, place=index + 1)
            for index, (user, max_score) in enumerate(rows)
        ]
