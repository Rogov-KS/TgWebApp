# Импорт всех моделей в правильном порядке
# User должен быть импортирован первым, так как другие модели зависят от него
from backend.entities.user.models import User
from backend.entities.game_session.models import GameSession
from backend.entities.refresh_token.models import RefreshToken
from backend.ows.auth.models import OAuth2Token

__all__ = [
    "User",
    "GameSession",
    "RefreshToken",
    "OAuth2Token",
]
