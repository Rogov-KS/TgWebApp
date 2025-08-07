import json
from typing import Annotated, Any
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import RedirectResponse

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

# Словарь для отслеживания обрабатываемых запросов
_processing_requests = {}


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

    # Защита от повторных запросов с тем же state
    request_key = f"{state}_{code}"
    if request_key in _processing_requests:
        logger.warning("Request already being processed: %s", request_key)
        raise HTTPException(
            status_code=429,
            detail="Request is already being processed"
        )

    _processing_requests[request_key] = True

    try:
        # Валидируем state
        if not state_storage.validate_state(state, "google"):
            logger.error("Invalid state parameter: %s", state)
            raise HTTPException(
                status_code=400,
                detail="Invalid state parameter"
            )

        google_token_url = "https://oauth2.googleapis.com/token"
        redirect_uri = "http://localhost:5173/auth/google"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=google_token_url,
                data={
                    "client_id": settings.OATH_GOOGLE_WEB_CLIENT_ID,
                    "client_secret": settings.OATH_GOOGLE_WEB_CLIENT_SECRET,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                    "code": code,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                ssl=False,
            ) as response:
                res = await response.json()
                # print(f"{res=}")
                id_token = res.get("id_token")
                access_token = res.get("access_token")
                # refresh_token = res.get("refresh_token")
                # Пока не используется
                user_data = jwt.decode(
                    id_token,
                    # key="",
                    algorithms=["RS256"],
                    options={"verify_signature": False},
                )

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url="https://www.googleapis.com/drive/v3/files",
                headers={
                    "Authorization": f"Bearer {access_token}"
                },
                ssl=False,
            ) as response:
                res2 = await response.json()
                print(f"res2={json.dumps(res2, indent=4, ensure_ascii=False)}")
                files = [item["name"] for item in res2["files"]]

        return {
            "user": user_data,
            "files": files,
        }
    finally:
        # Очищаем запись о запросе
        _processing_requests.pop(request_key, None)
