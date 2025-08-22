"""Интерфейсы для компонентов рейтинга игроков."""

from typing import List, Protocol

from backend.entities.assemblers.schemas import SLeaderboardPlace
from backend.entities.assemblers.schemas import SUser


class ILeaderboardDAO(Protocol):
    """Интерфейс для DAO рейтинга игроков."""

    async def get_leaderboard(
        self,
        limit: int = 10,
        offset: int = 0,
        sort_order: str = "desc",
    ) -> List[SLeaderboardPlace]:
        """Получить топ игроков по максимальному количеству очков."""


class ILeaderboardService(Protocol):
    """Интерфейс для сервиса рейтинга игроков."""

    async def get_leaderboard(
        self,
        limit: int = 10,
        offset: int = 0,
        sort_order: str = "desc",
    ) -> List[SLeaderboardPlace]:
        """Получить рейтинг игроков."""

    async def get_user_max_score(self, user: SUser) -> int | None:
        """Получить максимальный счет пользователя."""

    async def get_user_position_in_leaderboard(
        self, user: SUser
    ) -> int | None:
        """Получить позицию пользователя в общем рейтинге."""
