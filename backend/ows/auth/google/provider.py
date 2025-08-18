from typing import Any

import aiohttp
import jwt

from backend.core.config import settings
from backend.core.logger import get_logger
from backend.entities.oauth2_token.schemas import CloudFile, OAuth2UserData
from backend.ows.auth.base_provider import OAuth2Provider
from backend.ows.cloud_storage.google.drive import GoogleDriveIntegration

logger = get_logger(__name__)


class GoogleOAuth2Provider(OAuth2Provider):
    """Провайдер для Google OAuth2"""

    def __init__(self) -> None:
        super().__init__("google")
        self._drive_integration = GoogleDriveIntegration()
        self._public_keys = None

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

    async def _get_google_public_keys(self) -> dict[str, Any]:
        """Получить публичные ключи Google для проверки подписи id_token"""
        if self._public_keys is None:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://www.googleapis.com/oauth2/v1/certs", ssl=False
                    ) as response:
                        if response.status == 200:
                            self._public_keys = await response.json()
                        else:
                            logger.exception(
                                "Failed to fetch Google public keys",
                                exc_info=True,
                                extra={"status": response.status},
                            )
                            raise ValueError("Failed to fetch Google public keys")
            except Exception as e:
                logger.exception("Error fetching Google public keys", exc_info=True)
                raise ValueError(f"Error fetching Google public keys: {e}")

        return self._public_keys

    def _verify_google_id_token(self, id_token: str) -> dict[str, Any]:
        """Проверить подпись Google id_token"""
        try:
            # Декодируем заголовок токена для получения kid
            header = jwt.get_unverified_header(id_token)
            kid = header.get("kid")

            if not kid:
                raise ValueError("No 'kid' in token header")

            # Получаем публичные ключи
            public_keys = self._public_keys
            if not public_keys or kid not in public_keys:
                raise ValueError(f"Public key with kid '{kid}' not found")

            # Получаем публичный ключ
            public_key = public_keys[kid]

            # Декодируем и проверяем подпись токена
            payload = jwt.decode(
                id_token,
                public_key,
                algorithms=["RS256"],
                audience=self.client_id,  # Проверяем audience
                issuer=(
                    "https://accounts.google.com"  # Проверяем issuer
                ),
            )

            return payload

        except jwt.InvalidTokenError as e:
            logger.exception(
                "Invalid Google id_token", exc_info=True, extra={"id_token": id_token}
            )
            raise ValueError(f"Invalid Google id_token: {e}")
        except Exception as e:
            logger.exception(
                "Error verifying Google id_token",
                exc_info=True,
                extra={"id_token": id_token},
            )
            raise ValueError(f"Error verifying Google id_token: {e}")

    def get_authorization_params(self, state: str) -> dict[str, str]:
        return {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(
                [
                    "openid",
                    "profile",
                    "email",
                    "https://www.googleapis.com/auth/drive.readonly",
                ]
            ),
            "access_type": "offline",
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
        # Для Google, данные пользователя приходят в id_token
        id_token = raw_data.get("id_token")
        if not id_token:
            raise ValueError("No id_token in Google response")

        # TODO: Добавить проверку подписи id_token
        # # Получаем публичные ключи Google (если еще не получены)
        # if self._public_keys is None:
        #     await self._get_google_public_keys()

        # # Проверяем подпись id_token
        # try:
        #     user_info = self._verify_google_id_token(id_token)
        # except Exception as e:
        #     logger.exception("Error verifying Google id_token", exc_info=True, extra={"id_token": id_token})
        #     raise ValueError(f"Error verifying Google id_token: {e}")

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

    async def get_cloud_files(self, access_token: str) -> list[CloudFile]:
        """Получение файлов из Google Drive через интеграцию"""
        files = await self._drive_integration.get_files(access_token)
        return files


# Глобальный экземпляр
google_provider = GoogleOAuth2Provider()
