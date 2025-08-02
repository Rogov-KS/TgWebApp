from datetime import datetime

from pydantic import BaseModel, Field


class TelegramUserData(BaseModel):
    """Схема данных пользователя Telegram."""

    id: int = Field(..., description="ID пользователя в Telegram")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str | None = Field(None, description="Фамилия пользователя")
    username: str | None = Field(None, description="Username пользователя")
    language_code: str | None = Field(None, description="Код языка")
    is_premium: bool = Field(False, description="Премиум статус")
    photo_url: str | None = Field(None, description="URL фото профиля")


class TelegramInitData(BaseModel):
    """Схема для валидации initData."""

    init_data: str = Field(..., description="Строка initData от Telegram")


class TelegramAuthRequest(BaseModel):
    """Схема запроса авторизации через Telegram."""

    init_data: str = Field(..., description="Строка initData от Telegram")


class TelegramAuthResponse(BaseModel):
    """Схема ответа авторизации через Telegram."""

    access_token: str = Field(..., description="JWT токен доступа")
    token_type: str = Field("bearer", description="Тип токена")
    user: TelegramUserData = Field(..., description="Данные пользователя")


class TelegramValidationResponse(BaseModel):
    """Схема ответа валидации данных Telegram."""

    is_valid: bool = Field(..., description="Результат валидации")
    user_data: TelegramUserData | None = Field(None, description="Данные пользователя")
    error_message: str | None = Field(None, description="Сообщение об ошибке")


class TelegramWebAppData(BaseModel):
    """Схема данных Web App."""

    user_data: TelegramUserData | None = Field(None, description="Данные пользователя")
    chat_data: dict | None = Field(None, description="Данные чата")
    start_param: str | None = Field(None, description="Параметр запуска")
    auth_date: datetime = Field(..., description="Время авторизации")
    hash: str = Field(..., description="Хеш для проверки подлинности")
