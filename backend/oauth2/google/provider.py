from typing import Dict, Any, List
import jwt
import aiohttp

from backend.oauth2.base_provider import OAuth2Provider, OAuth2UserData, CloudFile
from backend.core.config import settings
from backend.logger import get_logger

logger = get_logger(__name__)


class GoogleOAuth2Provider(OAuth2Provider):
    """Провайдер для Google OAuth2"""
    
    def __init__(self):
        super().__init__("google")
    
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
                "https://www.googleapis.com/auth/drive.readonly",  # Доступ к Drive
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
        """Получение файлов из Google Drive"""
        drive_url = "https://www.googleapis.com/drive/v3/files"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=drive_url,
                headers={"Authorization": f"Bearer {access_token}"},
                params={
                    "fields": "files(id,name,size,mimeType,modifiedTime,webViewLink)",
                    "pageSize": 100
                },
                ssl=False,
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        "Failed to get Google Drive files. Status: %d, Response: %s",
                        response.status, error_text
                    )
                    return []
                
                data = await response.json()
                files = data.get("files", [])
                
                return [
                    CloudFile(
                        name=file.get("name", ""),
                        id=file.get("id"),
                        size=int(file.get("size", 0)) if file.get("size") else None,
                        mime_type=file.get("mimeType"),
                        modified_time=file.get("modifiedTime"),
                        download_url=file.get("webViewLink")
                    )
                    for file in files
                ]


# Глобальный экземпляр
google_provider = GoogleOAuth2Provider()