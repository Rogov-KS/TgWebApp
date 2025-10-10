"""Схемы для OAuth2 провайдеров"""

from typing import Any

from pydantic import BaseModel


class SOAuth2UserData(BaseModel):
    """Стандартизированные данные пользователя от OAuth2 провайдера"""

    provider_id: str  # ID пользователя в системе провайдера
    email: str
    first_name: str
    last_name: str | None = None
    username: str | None = None
    avatar_url: str | None = None
    provider_name: str = ""
    raw_data: dict[str, Any] | None = None


class SOAuth2TokenData(BaseModel):
    """Данные токенов от OAuth2 провайдера"""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"
    expires_in: int | None = None
    scope: str | None = None
    id_token: str | None = None
    raw_data: dict[str, Any] | None = None


class SCloudFile(BaseModel):
    """Информация о файле в облачном хранилище"""

    name: str
    id: str | None = None
    size: int | None = None
    mime_type: str | None = None
    modified_time: str | None = None
    download_url: str | None = None
