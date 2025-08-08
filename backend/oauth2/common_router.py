from typing import Annotated, Any, Dict
from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import RedirectResponse

from backend.oauth2.state_storage import state_storage
from backend.oauth2.google.provider import google_provider
from backend.oauth2.yandex.provider import yandex_provider
from backend.oauth2.base_provider import OAuth2Provider
from backend.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="",
    tags=["OAuth2/Common"],
)

# Реестр провайдеров
PROVIDERS: Dict[str, OAuth2Provider] = {
    "google": google_provider,
    "yandex": yandex_provider,
}


@router.get("/providers")
def get_available_providers() -> Dict[str, Any]:
    """Получить список доступных OAuth2 провайдеров"""
    return {
        "providers": list(PROVIDERS.keys()),
        "count": len(PROVIDERS)
    }


@router.get("/{provider}/url")
def get_oauth_redirect_uri(provider: str) -> RedirectResponse:
    """
    Получить URL для авторизации через указанного провайдера

    Args:
        provider: Имя провайдера (google, yandex)
    """
    if provider not in PROVIDERS:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Provider '{provider}' not found. "
                f"Available providers: {list(PROVIDERS.keys())}"
            )
        )

    oauth_provider = PROVIDERS[provider]
    state = state_storage.generate_state(provider)

    # Формируем URL авторизации
    auth_params = oauth_provider.get_authorization_params(state)
    url_params = "&".join([f"{k}={v}" for k, v in auth_params.items()])
    auth_url = f"{oauth_provider.authorization_url}?{url_params}"

    logger.info("Generated auth URL for %s: %s", provider, auth_url)
    return RedirectResponse(url=auth_url, status_code=302)


@router.post("/{provider}/callback")
async def handle_oauth_callback(
    provider: str,
    code: Annotated[str, Body()],
    state: Annotated[str, Body()],
) -> Dict[str, Any]:
    """
    Обработать callback от OAuth2 провайдера

    Args:
        provider: Имя провайдера (google, yandex)
        code: Authorization code от провайдера
        state: State для защиты от CSRF
    """
    if provider not in PROVIDERS:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Provider '{provider}' not found. "
                f"Available providers: {list(PROVIDERS.keys())}"
            )
        )

    logger.info("OAuth callback from %s\nCode: %s\nState: %s", provider, code, state)

    oauth_provider = PROVIDERS[provider]

    try:
        # Выполняем аутентификацию
        user_data, cloud_files = await oauth_provider.authenticate(code, state)

        logger.info("Authentication successful for %s: %s", provider, user_data.email)
        logger.info("Found %d cloud files", len(cloud_files))

        return {
            "provider": provider,
            "user": {
                "provider_id": user_data.provider_id,
                "email": user_data.email,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "username": user_data.username,
                "avatar_url": user_data.avatar_url,
                "provider_name": user_data.provider_name,
            },
            "cloud_files": [
                {
                    "name": file.name,
                    "id": file.id,
                    "size": file.size,
                    "mime_type": file.mime_type,
                    "modified_time": file.modified_time,
                    "download_url": file.download_url,
                }
                for file in cloud_files
            ],
            "files_count": len(cloud_files)
        }

    except Exception as e:
        logger.error("OAuth authentication failed for %s: %s", provider, str(e))
        raise HTTPException(
            status_code=400,
            detail=f"OAuth authentication failed: {str(e)}"
        )


@router.get("/{provider}/files")
async def get_cloud_files(
    provider: str,
    access_token: Annotated[str, Query()]
) -> Dict[str, Any]:
    """
    Получить файлы из облачного хранилища провайдера

    Args:
        provider: Имя провайдера (google, yandex)
        access_token: Access token для доступа к API
    """
    if provider not in PROVIDERS:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Provider '{provider}' not found. "
                f"Available providers: {list(PROVIDERS.keys())}"
            )
        )

    oauth_provider = PROVIDERS[provider]

    try:
        cloud_files = await oauth_provider.get_cloud_files(access_token)

        return {
            "provider": provider,
            "files": [
                {
                    "name": file.name,
                    "id": file.id,
                    "size": file.size,
                    "mime_type": file.mime_type,
                    "modified_time": file.modified_time,
                    "download_url": file.download_url,
                }
                for file in cloud_files
            ],
            "files_count": len(cloud_files)
        }

    except Exception as e:
        logger.error(
            "Failed to get cloud files from %s: %s", provider, str(e)
        )
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get cloud files: {str(e)}"
        )
