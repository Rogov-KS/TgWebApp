import json
from typing import Annotated, Any, Iterator, cast
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import RedirectResponse

from contextlib import contextmanager
import aiohttp
import jwt

from backend.oauth2.state_storage import state_storage
from backend.oauth2.google.utils import generate_google_oauth_redirect_uri
from backend.core.config import settings
from backend.logger import get_logger


router = APIRouter(
    prefix="/google",
    tags=["OAuth2/Google"],
)

logger = get_logger(__name__)

# Словарь для отслеживания обрабатываемых Google OAuth запросов
_google_processing_requests: dict[str, bool] = {}

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_DRIVE_FILES_URL = "https://www.googleapis.com/drive/v3/files"
GOOGLE_REDIRECT_URI = "http://localhost:5173/auth/google"


@contextmanager
def _single_processing_request(request_key: str) -> Iterator[None]:
    """
    Гарантирует, что запрос с тем же ключом
    обрабатывается только один раз.
    """
    if request_key in _google_processing_requests:
        logger.warning("Request already being processed: %s", request_key)
        raise HTTPException(
            status_code=429,
            detail="Request is already being processed",
        )
    _google_processing_requests[request_key] = True
    try:
        yield
    finally:
        _google_processing_requests.pop(request_key, None)


async def _exchange_code_for_tokens(code: str) -> dict[str, Any]:
    """Обменивает authorization code на токены у Google."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.OATH_GOOGLE_WEB_CLIENT_ID,
                "client_secret": settings.OATH_GOOGLE_WEB_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "code": code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            ssl=False,
        ) as response:
            data = await response.json()
            return cast(dict[str, Any], data)


def _decode_id_token(id_token: str) -> dict[str, Any]:
    """
    Декодирует id_token без проверки подписи
    (для демо/локальной отладки).
    """
    decoded = jwt.decode(
        id_token,
        algorithms=["RS256"],
        options={"verify_signature": False},
    )
    return cast(dict[str, Any], decoded)


async def fetch_google_drive_files(access_token: str) -> dict[str, Any]:
    """
    Возвращает список файлов из Google Drive
    для данного access_token.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url=GOOGLE_DRIVE_FILES_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            ssl=False,
        ) as response:
            files_payload = await response.json()
            logger.debug(
                "Drive API response: %s",
                json.dumps(files_payload, indent=4, ensure_ascii=False),
            )
            return cast(dict[str, Any], files_payload)


async def _fetch_drive_file_names(access_token: str) -> list[str]:
    '''
    Возвращает список имен файлов из Google Drive
    для данного access_token.
    '''
    files_payload = await fetch_google_drive_files(access_token)
    return [item["name"] for item in files_payload.get("files", [])]


@router.get("/url")
def get_google_oauth_redirect_uri() -> RedirectResponse:
    '''
    Get Google OAuth redirect URI

    Returns:
        RedirectResponse: Redirect to Google OAuth redirect URI
    '''
    # Генерируем state и сохраняем его
    state = state_storage.generate_state("google")
    uri = generate_google_oauth_redirect_uri(state)
    logger.info("call google /url : %s \n", uri)
    return RedirectResponse(url=uri, status_code=302)


@router.post("/callback")
async def handle_code(
    code: Annotated[str, Body()],
    state: Annotated[str, Body()],
) -> dict[str, Any]:
    '''
    Handle Google OAuth callback

    Args:
        code: Authorization code
        state: State
    '''
    logger.info("call google /callback : %s \n %s \n\n", code, state)

    request_key = f"{state}_{code}"
    with _single_processing_request(request_key):
        state_storage.validate_state_or_raise(state, "google")

        tokens_payload = await _exchange_code_for_tokens(code)
        logger.info("tokens_payload: %s", tokens_payload)
        id_token = tokens_payload.get("id_token")
        logger.info("id_token: %s", id_token)
        access_token = tokens_payload.get("access_token")
        logger.info("access_token: %s", access_token)
        user_data = _decode_id_token(id_token) if id_token else {}
        logger.info("user_data: %s", user_data)
        files = (
            await _fetch_drive_file_names(access_token)
            if access_token
            else []
        )
        logger.info("files: %s", files)
        return {"user": user_data, "files": files}
