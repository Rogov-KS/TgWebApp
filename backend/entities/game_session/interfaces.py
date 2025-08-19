"""Интерфейсы для компонентов игровых сессий."""

from typing import Any, List, Protocol

from backend.entities.game_session.models import (
    GameSession as GameSessionModel,
)
from backend.entities.game_session.schemas import (
    GameSession as GameSessionSchema,
)


class IGameSessionDAO(Protocol):
    """Интерфейс для DAO игровых сессий."""

    async def get_all(self, **filter_by: Any) -> List[GameSessionModel]:
        """Получить все записи игровых сессий."""

    async def get_one_or_none(
        self, **filter_by: Any
    ) -> GameSessionModel | None:
        """Получить игровую сессию по фильтру или None."""

    async def create(self, **data: Any) -> GameSessionModel | None:
        """Создать новую игровую сессию."""

    async def delete(self, **filter_by: Any) -> bool:
        """Удалить игровую сессию."""

    async def update(
        self,
        filters: dict[str, Any],
        update_data: dict[str, Any],
    ) -> GameSessionModel | None:
        """Обновить игровую сессию."""

    async def get_max_score(self, user_id: int) -> int | None:
        """Получить максимальный счет пользователя."""


class IGameSessionService(Protocol):
    """Интерфейс для сервиса игровых сессий."""

    async def get_all_game_sessions(self) -> List[GameSessionSchema]:
        """Получить все игровые сессии."""

    async def get_user_game_sessions(
        self, user_id: int
    ) -> List[GameSessionSchema]:
        """Получить все игровые сессии пользователя."""

    async def get_game_session_by_id(
        self, game_session_id: int, user: Any
    ) -> GameSessionSchema:
        """Получить игровую сессию по ID с проверкой доступа."""

    async def create_game_session(
        self, game_session_data: Any, user: Any
    ) -> GameSessionSchema:
        """Создать новую игровую сессию."""

    async def update_game_session(
        self,
        game_session_id: int,
        game_session_update: Any,
        user: Any,
    ) -> GameSessionSchema:
        """Обновить игровую сессию."""

    async def delete_game_session(
        self, game_session_id: int, user: Any
    ) -> bool:
        """Удалить игровую сессию."""
