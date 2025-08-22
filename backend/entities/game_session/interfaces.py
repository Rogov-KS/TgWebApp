"""Интерфейсы для компонентов игровых сессий."""

from typing import Any, List, Protocol

from backend.core.base_dao import IBaseDAO
from backend.entities.assemblers.schemas import SGameSession
from backend.entities.game_session.models import GameSessionDB


class IGameSessionDAO(IBaseDAO[GameSessionDB]):
    """Интерфейс для DAO игровых сессий."""
    # Базовые методы уже определены в IBaseDAO

    async def get_max_score(self, user_id: int) -> int | None:
        """Получить максимальный счет пользователя."""


class IGameSessionService(Protocol):
    """Интерфейс для сервиса игровых сессий."""

    async def get_all_game_sessions(self) -> List[SGameSession]:
        """Получить все игровые сессии."""

    async def get_user_game_sessions(
        self, user_id: int
    ) -> List[SGameSession]:
        """Получить все игровые сессии пользователя."""

    async def get_game_session_by_id(
        self, game_session_id: int, user: Any
    ) -> SGameSession:
        """Получить игровую сессию по ID с проверкой доступа."""

    async def create_game_session(
        self, game_session_data: Any, user: Any
    ) -> SGameSession:
        """Создать новую игровую сессию."""

    async def update_game_session(
        self,
        game_session_id: int,
        game_session_update: Any,
        user: Any,
    ) -> SGameSession:
        """Обновить игровую сессию."""

    async def delete_game_session(
        self, game_session_id: int, user: Any
    ) -> bool:
        """Удалить игровую сессию."""
