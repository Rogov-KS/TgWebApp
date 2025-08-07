import json
from typing import Annotated, Any
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

# Словарь для отслеживания обрабатываемых запросов
_processing_requests = {}


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


async def get_yandex_user_data(access_token: str) -> dict[str, Any]:
    '''
    Get user data from Yandex using their recommended API endpoint

    Args:
        access_token: OAuth access token from Yandex

    Returns:
        dict: User data from Yandex

    Raises:
        HTTPException: If failed to get user data
    '''
    yandex_user_info_url = "https://login.yandex.ru/info"

    async with aiohttp.ClientSession() as session:
        async with session.get(
            url=yandex_user_info_url,
            headers={
                "Authorization": f"OAuth {access_token}",
                "Content-Type": "application/json"
            },
            params={"format": "json"},
            ssl=False,
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(
                    "Failed to get Yandex user data. Status: %d, Response: %s",
                    response.status, error_text
                )
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to get user data from Yandex: "
                           f"{error_text}"
                )

            user_data = await response.json()
            logger.info(
                "Successfully retrieved user data from Yandex: %s", user_data
            )
            return user_data


@router.post("/callback")
async def handle_code(
    code: Annotated[str, Body()],
    state: Annotated[str, Body()],
) -> Any:
    '''
    Handle Yandex OAuth callback

    Args:
        code: Authorization code
        state: State
    '''
    logger.info("handle_code from Yandex\nCode: %s\nState: %s", code, state)

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
        if not state_storage.validate_state(state, "yandex"):
            logger.error("Invalid state parameter: %s", state)
            raise HTTPException(
                status_code=400,
                detail="Invalid state parameter"
            )

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
                res = await response.json()
                # print(f"{res=}")
                access_token = res.get("access_token")
                # refresh_token = res.get("refresh_token")
                # Пока не используется

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url="https://login.yandex.ru/info",
                headers={
                    "Authorization": f"OAuth {access_token}"
                },
                ssl=False,
            ) as response:
                res2 = await response.json()
                print(f"res2={json.dumps(res2, indent=4, ensure_ascii=False)}")

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
                res3 = await response.json()
                print(f"res3={json.dumps(res3, indent=4, ensure_ascii=False)}")

        return {
            "user": res2,
            "access_token": access_token,
        }  # type: ignore
    finally:
        # Очищаем запись о запросе
        _processing_requests.pop(request_key, None)
