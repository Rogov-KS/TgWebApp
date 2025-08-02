# Импорт всех моделей
from backend.models.achievements import Achievement
from backend.models.game_session import GameSession
from backend.models.game_settings import GameSettings
from backend.models.telegram_webapp_data import TelegramWebAppData
from backend.models.user import User
from backend.models.user_achievements import UserAchievement
from backend.models.refresh_token import RefreshToken

__all__ = [
    "Achievement",
    "GameSession",
    "GameSettings",
    "TelegramWebAppData",
    "User",
    "UserAchievement",
    "RefreshToken",
]
