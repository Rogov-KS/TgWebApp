from datetime import datetime
from typing import Any

from pydantic import BaseModel


class GameSessionBase(BaseModel):
    """Базовая схема игровой сессии."""
    user_id: int
    level: int = 1
    score: int = 0
    duration: int = 0
    is_completed: bool = False
    game_data: dict[str, Any] | None = None


class GameSessionCreate(GameSessionBase):
    """Схема для создания игровой сессии."""


class GameSessionUpdate(BaseModel):
    """Схема для обновления игровой сессии."""
    score: int
    duration: int
    is_completed: bool
    game_data: dict[str, Any] | None = None


class GameSession(GameSessionBase):
    """Схема игровой сессии для ответов."""
    id: int
    started_at: datetime
    ended_at: datetime | None = None

    class Config:
        from_attributes = True
