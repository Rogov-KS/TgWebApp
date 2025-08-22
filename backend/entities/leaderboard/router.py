from fastapi import APIRouter
from fastapi_cache.decorator import cache
from fastapi_versioning import version

from backend.core.dependecies import CurrentUserDep
from backend.entities.assemblers.schemas import SLeaderboardPlace
from backend.entities.leaderboard.service import LeaderboardServiceDep

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("/")
@version(1)
@cache(expire=60)
async def get_leaderboard(
    leaderboard_service: LeaderboardServiceDep,
    limit: int = 10,
    offset: int = 0,
    sort_order: str = "desc",
) -> list[SLeaderboardPlace]:
    """Получить топ игроков в рейтинге."""
    return await leaderboard_service.get_leaderboard(limit, offset, sort_order)


@router.get("/my_max_score")
@version(1)
@cache(expire=60)
async def get_my_max_score(
    leaderboard_service: LeaderboardServiceDep,
    user: CurrentUserDep,
) -> int | None:
    """Получить максимальный счет текущего пользователя."""
    return await leaderboard_service.get_user_max_score(user)


@router.get("/my_position")
@version(1)
@cache(expire=120)
async def get_my_position(
    leaderboard_service: LeaderboardServiceDep,
    user: CurrentUserDep,
) -> int | None:
    """Получить позицию текущего пользователя в рейтинге."""
    return await leaderboard_service.get_user_position_in_leaderboard(user)
