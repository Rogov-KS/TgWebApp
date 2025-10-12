"""Модуль для авторизации через Telegram."""

from backend.entities.telegram.router import router as telegram_router
from backend.entities.telegram.schemas import (
    TelegramInitData,
    TelegramUserData,
)
from backend.entities.telegram.service import TelegramAuthService
from backend.entities.telegram.utils import (
    extract_user_data_from_init_data,
    is_telegram_data_fresh,
    parse_telegram_init_data,
    validate_telegram_init_data,
)

__all__ = [
    "TelegramAuthService",
    "TelegramInitData",
    "TelegramUserData",
    "extract_user_data_from_init_data",
    "is_telegram_data_fresh",
    "parse_telegram_init_data",
    "telegram_router",
    "validate_telegram_init_data",
]
