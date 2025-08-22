# Импорт всех моделей в правильном порядке
# UserDB должен быть импортирован первым, так как другие модели зависят от него
from backend.entities.user.models import UserDB
from backend.entities.game_session.models import GameSessionDB
from backend.entities.refresh_token.models import RefreshTokenDB
from backend.ows.auth.models import OAuth2TokenDB

__all__ = [
    "UserDB",
    "GameSessionDB",
    "RefreshTokenDB",
    "OAuth2TokenDB",
]
