import json
from typing import Annotated, Any, cast
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import RedirectResponse

import aiohttp

from backend.oauth2.state_storage import state_storage
from backend.oauth2.yandex.utils import generate_yandex_oauth_redirect_uri
from backend.core.config import settings
from backend.logger import get_logger


router = APIRouter(
    prefix="/yandex",
    tags=["OAuth2/Yandex"],
)

logger = get_logger(__name__)

# Словарь для отслеживания обрабатываемых Yandex OAuth запросов
_yandex_processing_requests: dict[str, bool] = {}


@router.get("/url")
def get_yandex_oauth_redirect_uri() -> RedirectResponse:
    '''
    Get Yandex OAuth redirect URI

    Returns:
        RedirectResponse: Redirect to Yandex OAuth redirect URI
    '''
    # Генерируем state и сохраняем его
    state = state_storage.generate_state("yandex")
    uri = generate_yandex_oauth_redirect_uri(state)
    logger.info("call yandex /url : %s \n", uri)
    return RedirectResponse(url=uri, status_code=302)


async def fetch_yandex_user_data(access_token: str) -> dict[str, Any]:
    '''
    Выполняет HTTP-запрос к API Яндекса для получения данных пользователя.
    Возвращает «сырые» данные ответа.
    '''
    yandex_user_info_url = "https://login.yandex.ru/info"

    async with aiohttp.ClientSession() as session:
        async with session.get(
            url=yandex_user_info_url,
            headers={
                "Authorization": f"OAuth {access_token}",
                "Content-Type": "application/json",
            },
            params={"format": "json"},
            ssl=False,
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(
                    "Failed to get Yandex user data. Status: %d, Response: %s",
                    response.status,
                    error_text,
                )
                raise HTTPException(
                    status_code=response.status,
                    detail=(
                        f"Failed to get user data from Yandex: {error_text}"
                    ),
                )

            user_data = await response.json()
            logger.info(
                "Successfully retrieved user data from Yandex: %s",
                user_data,
            )
            return cast(dict[str, Any], user_data)


async def fetch_yandex_disk_files(access_token: str) -> dict[str, Any]:
    '''
    Возвращает список файлов из Яндекс.Диска
    для данного access_token.

    Args:
        access_token: OAuth токен для доступа к Яндекс.Диску

    Returns:
        dict: Ответ от API Яндекс.Диска с информацией о файлах

    Raises:
        HTTPException: При ошибке запроса к API
    '''
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url="https://cloud-api.yandex.net/v1/disk/resources",
            params={"path": "/"},
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
                    "Failed to get Yandex.Disk files. "
                    "Status: %d, Response: %s",
                    response.status,
                    error_text,
                )
                raise HTTPException(
                    status_code=response.status,
                    detail=(
                        f"Failed to get files from Yandex.Disk: {error_text}"
                    ),
                )

            files_payload = await response.json()
            logger.debug(
                "Yandex.Disk API response: %s",
                json.dumps(files_payload, indent=4, ensure_ascii=False),
            )
            return cast(dict[str, Any], files_payload)


async def _fetch_disk_file_names(access_token: str) -> list[str]:
    '''
    Возвращает список имен файлов из Яндекс.Диска
    для данного access_token.

    Args:
        access_token: OAuth токен для доступа к Яндекс.Диску

    Returns:
        list[str]: Список имен файлов
    '''
    files_payload = await fetch_yandex_disk_files(access_token)
    # Извлекаем имена файлов из ответа Яндекс.Диска
    embedded = files_payload.get("_embedded", {})
    items = embedded.get("items", [])
    return [item.get("name", "") for item in items if item.get("name")]


async def _exchange_code_for_token(code: str) -> str:
    '''
    Обменивает authorization code на access token у Yandex.

    Args:
        code: Authorization code от Yandex

    Returns:
        str: Access token

    Raises:
        HTTPException: При ошибке получения токена
    '''
    yandex_token_url = "https://oauth.yandex.ru/token"
    redirect_uri = "http://localhost:5173/auth/yandex"

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=yandex_token_url,
            data={
                "client_id": settings.OATH_YANDEX_WEB_CLIENT_ID,
                "client_secret": settings.OATH_YANDEX_WEB_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
                "code": code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            ssl=False,
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(
                    "Failed to get Yandex access token. "
                    "Status: %d, Response: %s",
                    response.status,
                    error_text,
                )
                raise HTTPException(
                    status_code=response.status,
                    detail=(
                        f"Failed to get access token from Yandex: "
                        f"{error_text}"
                    ),
                )

            res = await response.json()
            access_token = res.get("access_token")

            if not access_token:
                logger.error("No access token in Yandex response: %s", res)
                raise HTTPException(
                    status_code=400,
                    detail="No access token received from Yandex",
                )

            return str(access_token)


def process_yandex_user_data(user_data: dict[str, Any]) -> dict[str, Any]:
    '''
    Пост-обработка данных пользователя из Яндекса.
    Пока просто возвращает как есть, но здесь можно нормализовать
    поля под нужды фронтенда/БД.
    '''
    return user_data


@router.post("/callback")
async def handle_code(
    code: Annotated[str, Body()],
    state: Annotated[str, Body()],
) -> dict[str, Any]:
    '''
    Handle Yandex OAuth callback

    Args:
        code: Authorization code
        state: State
    '''
    logger.info("handle_code from Yandex\nCode: %s\nState: %s", code, state)

    # Защита от повторных запросов с тем же state
    request_key = f"{state}_{code}"
    if request_key in _yandex_processing_requests:
        logger.warning("Request already being processed: %s", request_key)
        raise HTTPException(
            status_code=429,
            detail="Request is already being processed"
        )

    _yandex_processing_requests[request_key] = True

    try:
        # Валидируем state
        state_storage.validate_state_or_raise(state, "yandex")

        # Получаем access token через отдельную функцию
        access_token = await _exchange_code_for_token(code)

        # Запрос к API Яндекса и дальнейшая обработка
        # вынесены в отдельные функции
        logger.info("access_token: %s", access_token)
        raw_user = await fetch_yandex_user_data(access_token)
        logger.info("raw_user: %s", raw_user)
        user = process_yandex_user_data(raw_user)
        logger.info("user: %s", user)
        files = (
            await _fetch_disk_file_names(access_token)
            if access_token
            else []
        )
        logger.info("files: %s", files)
        return {
            "user": user,
            "files": files,
        }
    finally:
        # Очищаем запись о запросе
        _yandex_processing_requests.pop(request_key, None)
