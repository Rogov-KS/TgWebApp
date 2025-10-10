# Импорт всех моделей в правильном порядке
# UserDB должен быть импортирован первым, так как другие модели зависят от него
from backend.entities.game_session.models import GameSessionDB
from backend.entities.refresh_token.models import RefreshTokenDB
from backend.entities.user.models import UserDB
from backend.integrations.oauth.models import OAuth2TokenDB

__all__ = [
    "GameSessionDB",
    "OAuth2TokenDB",
    "RefreshTokenDB",
    "UserDB",
]
