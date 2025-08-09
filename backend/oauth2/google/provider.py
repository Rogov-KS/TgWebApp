from typing import Dict, Any, List
import jwt

from backend.oauth2.base_provider import OAuth2Provider
from backend.core.config import settings
from backend.logger import get_logger
from backend.oauth2_integrations.google.drive import GoogleDriveIntegration
from backend.schemas import CloudFile, OAuth2UserData

logger = get_logger(__name__)


class GoogleOAuth2Provider(OAuth2Provider):
    """Провайдер для Google OAuth2"""

    def __init__(self) -> None:
        super().__init__("google")
        self._drive_integration = GoogleDriveIntegration()

    @property
    def client_id(self) -> str:
        return settings.OATH_GOOGLE_WEB_CLIENT_ID

    @property
    def client_secret(self) -> str:
        return settings.OATH_GOOGLE_WEB_CLIENT_SECRET

    @property
    def redirect_uri(self) -> str:
        return "http://localhost:5173/auth/google"

    @property
    def authorization_url(self) -> str:
        return "https://accounts.google.com/o/oauth2/v2/auth"

    @property
    def token_url(self) -> str:
        return "https://oauth2.googleapis.com/token"

    @property
    def user_info_url(self) -> str:
        # Google предоставляет данные пользователя через id_token
        return ""

    def get_authorization_params(self, state: str) -> Dict[str, str]:
        return {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join([
                "openid",
                "profile",
                "email",
                "https://www.googleapis.com/auth/drive.readonly",
            ]),
            "access_type": "offline",
            "state": state,
        }

    def get_token_params(self, code: str) -> Dict[str, str]:
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
            "code": code,
        }

    def parse_user_data(self, raw_data: Dict[str, Any]) -> OAuth2UserData:
        # Для Google, данные пользователя приходят в id_token
        id_token = raw_data.get("id_token")
        if not id_token:
            raise ValueError("No id_token in Google response")

        # Декодируем id_token без проверки подписи (для демо)
        user_info = jwt.decode(
            id_token,
            algorithms=["RS256"],
            options={"verify_signature": False},
        )

        return OAuth2UserData(
            provider_id=user_info.get("sub", ""),
            email=user_info.get("email", ""),
            first_name=user_info.get("given_name", ""),
            last_name=user_info.get("family_name"),
            username=user_info.get("name"),
            avatar_url=user_info.get("picture"),
            provider_name="google",
            raw_data=user_info,
        )

    async def get_cloud_files(self, access_token: str) -> List[CloudFile]:
        """Получение файлов из Google Drive через интеграцию"""
        files = await self._drive_integration.get_files(access_token)
        return files


# Глобальный экземпляр
google_provider = GoogleOAuth2Provider()