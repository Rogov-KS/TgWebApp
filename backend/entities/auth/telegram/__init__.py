"""Модуль для авторизации через Telegram."""

from .router import router as telegram_router
from .schemas import (
    TelegramAuthRequest,
    TelegramAuthResponse,
    TelegramInitData,
    TelegramUserData,
)
from .service import TelegramAuthService
from .utils import (
    extract_user_data_from_init_data,
    is_telegram_data_fresh,
    parse_telegram_init_data,
    validate_telegram_init_data,
)

__all__ = [
    "telegram_router",
    "TelegramAuthService",
    "TelegramAuthRequest",
    "TelegramAuthResponse",
    "TelegramInitData",
    "TelegramUserData",
    "parse_telegram_init_data",
    "validate_telegram_init_data",
    "is_telegram_data_fresh",
    "extract_user_data_from_init_data",
]
