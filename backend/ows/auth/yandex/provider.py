from typing import Annotated, Any

from fastapi import Depends

from backend.core.config import settings
from backend.core.database import get_async_session
from backend.core.logger import get_logger
from backend.entities.user.dao import UserDAODep, get_user_dao
from backend.entities.refresh_token.dao import RefreshTokenDAODep, get_refresh_token_dao
from backend.ows.auth.dao import OAuth2TokenDAODep, get_oauth2_token_dao
from backend.entities.assemblers.schemas import CloudFile, OAuth2UserData
from backend.ows.auth.service import OAuth2Service
from backend.ows.cloud_storage.yandex.disk import YandexDiskIntegration

logger = get_logger(__name__)


class YandexOAuth2Service(OAuth2Service):
    """Провайдер для Yandex OAuth2"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(provider_name="yandex", *args, **kwargs)
        self._disk_integration = YandexDiskIntegration()

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

    async def parse_user_data(self, raw_data: dict[str, Any]) -> OAuth2UserData:
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
        """Получение файлов из Яндекс.Диска через интеграцию"""
        files = await self._disk_integration.get_files(access_token)
        return files


def get_yandex_oauth2_service(
    oauth2_token_dao: OAuth2TokenDAODep,
    user_dao: UserDAODep,
    refresh_token_dao: RefreshTokenDAODep
) -> YandexOAuth2Service:
    return YandexOAuth2Service(
        oauth2_token_dao=oauth2_token_dao,
        user_dao=user_dao,
        refresh_token_dao=refresh_token_dao
    )


# Тип для использования в роутерах
YandexOAuth2ServiceDep = Annotated[
    YandexOAuth2Service, Depends(get_yandex_oauth2_service)
]
