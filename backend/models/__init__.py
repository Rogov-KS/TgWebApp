# Импорт всех моделей
from backend.models.game_session import GameSession
from backend.models.oauth2_token import OAuth2Token
from backend.models.user import User

__all__ = [
    "GameSession",
    "OAuth2Token",
    "User",
]
