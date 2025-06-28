from backend.dao.base import BaseDAO
from backend.models.game_session import GameSession as GameSessionDB


class GameSessionDAO(BaseDAO[GameSessionDB]):
    """DAO для работы с игровыми сессиями."""

    model = GameSessionDB
