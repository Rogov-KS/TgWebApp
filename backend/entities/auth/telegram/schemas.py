"""Схемы для Telegram авторизации."""

from typing import Optional

from pydantic import BaseModel, Field


class TelegramUserData(BaseModel):
    """Данные пользователя из Telegram."""

    id: int = Field(
        ..., description="Уникальный идентификатор пользователя в Telegram"
    )
    first_name: str = Field(..., description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    username: Optional[str] = Field(
        None, description="Имя пользователя в Telegram"
    )
    language_code: Optional[str] = Field(
        None, description="Код языка пользователя"
    )
    is_premium: Optional[bool] = Field(
        None, description="Является ли пользователь Premium"
    )
    photo_url: Optional[str] = Field(
        None, description="URL фотографии пользователя"
    )


class TelegramInitData(BaseModel):
    """Данные инициализации Telegram Mini App."""

    user: Optional[TelegramUserData] = Field(
        None, description="Данные пользователя"
    )
    chat_instance: Optional[str] = Field(
        None, description="Идентификатор чата"
    )
    chat_type: Optional[str] = Field(None, description="Тип чата")
    auth_date: int = Field(
        ..., description="Время авторизации (Unix timestamp)"
    )
    hash: str = Field(..., description="Хеш для проверки подлинности данных")


class TelegramAuthRequest(BaseModel):
    """Запрос на авторизацию через Telegram."""

    init_data: str = Field(
        ..., description="Строка initData от Telegram Mini App"
    )


class TelegramAuthResponse(BaseModel):
    """Ответ на авторизацию через Telegram."""

    access_token: str = Field(..., description="JWT токен доступа")
    refresh_token: str = Field(..., description="JWT токен обновления")
    token_type: str = Field(default="bearer", description="Тип токена")
    user: dict = Field(..., description="Данные пользователя")
