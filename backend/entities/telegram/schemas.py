"""Схемы для Telegram авторизации."""

from pydantic import BaseModel, Field


class TelegramUserData(BaseModel):
    """Данные пользователя из Telegram."""

    id: int = Field(
        ..., description="Уникальный идентификатор пользователя в Telegram"
    )
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str | None = Field(None, description="Фамилия пользователя")
    username: str | None = Field(
        None, description="Имя пользователя в Telegram"
    )
    language_code: str | None = Field(
        None, description="Код языка пользователя"
    )
    is_premium: bool | None = Field(
        None, description="Является ли пользователь Premium"
    )
    photo_url: str | None = Field(
        None, description="URL фотографии пользователя"
    )


class TelegramInitData(BaseModel):
    """Данные инициализации Telegram Mini App."""

    user: TelegramUserData | None = Field(
        None, description="Данные пользователя"
    )
    chat_instance: str | None = Field(
        None, description="Идентификатор чата"
    )
    chat_type: str | None = Field(None, description="Тип чата")
    auth_date: int = Field(
        ..., description="Время авторизации (Unix timestamp)"
    )
    hash: str = Field(..., description="Хеш для проверки подлинности данных")


class TelegramAuthRequest(BaseModel):
    """Запрос авторизации через Telegram."""

    init_data: str = Field(
        ...,
        description="Строка initData от Telegram Mini App"
    )
