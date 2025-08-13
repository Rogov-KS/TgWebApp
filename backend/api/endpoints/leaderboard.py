from fastapi import APIRouter, Depends
from fastapi_cache.decorator import cache
from fastapi_versioning import version

from backend.core.dependecies import get_current_user
from backend.dao.game_session import GameSessionDAO
from backend.dao.utils import get_db_leaderboard
from backend.schemas.leaderboard import LeaderboardPlace
from backend.schemas.user import User

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("/")
@version(1)
@cache(expire=60)
async def get_leaderboard(
    limit: int = 10,
    offset: int = 0,
    sort_order: str = "desc",
) -> list[LeaderboardPlace]:
    """Получить топ игроков в рейтинге."""
    top_scores = await get_db_leaderboard(limit, offset, sort_order)
    return top_scores


@router.get("/my_max_score")
@version(1)
@cache(expire=60)
async def get_my_max_score(
    user: User = Depends(get_current_user),
) -> int | None:
    """Получить максимальный счет пользователя."""
    max_score = await GameSessionDAO.get_max_score(user.id)
    return max_score
