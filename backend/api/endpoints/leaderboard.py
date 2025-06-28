from fastapi import APIRouter

from backend.dao.utils import get_db_leaderboard
from backend.schemas.leaderboard import LeaderboardPlace

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("/")
async def get_leaderboard(
    limit: int = 10,
    offset: int = 0,
    sort_order: str = "desc",
) -> list[LeaderboardPlace]:
    """Получить топ игроков в рейтинге."""
    top_scores = await get_db_leaderboard(limit, offset, sort_order)
    return top_scores
