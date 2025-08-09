from typing import Any

import aiohttp

from backend.core.config import settings
from backend.logger import get_logger
from backend.oauth2.base_provider import CloudFile, OAuth2Provider, OAuth2UserData

logger = get_logger(__name__)


class YandexOAuth2Provider(OAuth2Provider):
    """Провайдер для Yandex OAuth2"""

    def __init__(self) -> None:
        super().__init__("yandex")

    @property
    def client_id(self) -> str:
        return settings.OATH_YANDEX_WEB_CLIENT_ID

    @property
    def client_secret(self) -> str:
        return settings.OATH_YANDEX_WEB_CLIENT_SECRET

    @property
    def redirect_uri(self) -> str:
        return "http://localhost:5173/auth/yandex"

    @property
    def authorization_url(self) -> str:
        return "https://oauth.yandex.ru/authorize"

    @property
    def token_url(self) -> str:
        return "https://oauth.yandex.ru/token"

    @property
    def user_info_url(self) -> str:
        return "https://login.yandex.ru/info"

    def get_authorization_params(self, state: str) -> dict[str, str]:
        return {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(
                [
                    "login:email",
                    "login:info",
                    "cloud_api:disk.read",  # Доступ к Яндекс.Диску
                ]
            ),
            "state": state,
        }

    def get_token_params(self, code: str) -> dict[str, str]:
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "code": code,
        }

    def parse_user_data(self, raw_data: dict[str, Any]) -> OAuth2UserData:
        """Парсинг данных пользователя из ответа Yandex API"""
        return OAuth2UserData(
            provider_id=raw_data.get("id", ""),
            email=raw_data.get("default_email", ""),
            first_name=raw_data.get("first_name", ""),
            last_name=raw_data.get("last_name"),
            username=raw_data.get("login"),
            avatar_url=self._get_avatar_url(raw_data),
            provider_name="yandex",
            raw_data=raw_data,
        )

    def _get_avatar_url(self, user_data: dict[str, Any]) -> str:
        """Формирует URL аватара пользователя"""
        avatar_id = user_data.get("default_avatar_id")
        if avatar_id:
            return f"https://avatars.yandex.net/get-yapic/{avatar_id}/islands-200"
        return ""

    async def get_cloud_files(self, access_token: str) -> list[CloudFile]:
        """Получение файлов из Яндекс.Диска"""
        disk_url = "https://cloud-api.yandex.net/v1/disk/resources/files"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=disk_url,
                params={
                },
                headers={
                    "Authorization": f"OAuth {access_token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                ssl=False,
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        "Failed to get Yandex.Disk files. " "Status: %d, Response: %s",
                        response.status,
                        error_text,
                    )
                    return []

                data = await response.json()
                items = data.get("items", [])

                return [
                    CloudFile(
                        name=item.get("name", ""),
                        id=item.get("resource_id"),
                        size=item.get("size"),
                        mime_type=item.get("mime_type"),
                        modified_time=item.get("modified"),
                        download_url=item.get("file"),  # Прямая ссылка на скачивание
                    )
                    for item in items
                    if item.get("type") == "file"  # Только файлы, не папки
                ]


# Глобальный экземпляр
yandex_provider = YandexOAuth2Provider()
