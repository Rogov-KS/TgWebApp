"""Интерфейсы для компонентов рейтинга игроков."""

from typing import List, Protocol

from backend.entities.leaderboard.schemas import LeaderboardPlace
from backend.entities.user.schemas import User


class ILeaderboardDAO(Protocol):
    """Интерфейс для DAO рейтинга игроков."""

    async def get_leaderboard(
        self,
        limit: int = 10,
        offset: int = 0,
        sort_order: str = "desc",
    ) -> List[LeaderboardPlace]:
        """Получить топ игроков по максимальному количеству очков."""


class ILeaderboardService(Protocol):
    """Интерфейс для сервиса рейтинга игроков."""

    async def get_leaderboard(
        self,
        limit: int = 10,
        offset: int = 0,
        sort_order: str = "desc",
    ) -> List[LeaderboardPlace]:
        """Получить рейтинг игроков."""

    async def get_user_max_score(self, user: User) -> int | None:
        """Получить максимальный счет пользователя."""

    async def get_user_position_in_leaderboard(
        self, user: User
    ) -> int | None:
        """Получить позицию пользователя в общем рейтинге."""
