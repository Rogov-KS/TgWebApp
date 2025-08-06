from typing import Annotated, Any
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import RedirectResponse

import aiohttp
import jwt

# from state_storage import state_storage
from backend.oauth2.yandex.utils import generate_yandex_oauth_redirect_uri
from backend.core.config import settings
from backend.logger import get_logger


router = APIRouter(
    prefix="/yandex",
    tags=["OAuth2/Yandex"],
)

logger = get_logger(__name__)


@router.get("/url")
def get_yandex_oauth_redirect_uri() -> RedirectResponse:
    '''
    Get Yandex OAuth redirect URI

    Returns:
        RedirectResponse: Redirect to Yandex OAuth redirect URI
    '''
    uri = generate_yandex_oauth_redirect_uri()
    logger.info("get_yandex_oauth_redirect_uri into %s", uri)
    return RedirectResponse(url=uri, status_code=303)


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
) -> dict[str, Any]:
    '''
    Handle Yandex OAuth callback

    Args:
        code: Authorization code
        state: State
    '''
    logger.info("handle_code from Yandex\nCode: %s\nState: %s", code, state)
    # if state not in state_storage:
    #     raise
    # else:
    #     print("Стейт корректный")
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
                    "Failed to get access token from Yandex. Status: %d, "
                    "Response: %s",
                    response.status, error_text
                )
                raise HTTPException(
                    status_code=response.status,
                    detail=f"Failed to get access token from Yandex: "
                           f"{error_text}"
                )

            res = await response.json()
            logger.info("Token response from Yandex: %s", res)
            access_token = res.get("access_token")
            refresh_token = res.get("refresh_token")

            if not access_token:
                raise HTTPException(
                    status_code=400,
                    detail="No access token received from Yandex"
                )

            # Get user data using the access token
            try:
                user_data = await get_yandex_user_data(access_token)
            except HTTPException:
                raise
            except Exception as e:
                logger.error(
                    "Unexpected error while getting user data: %s", str(e)
                )
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to get user data: {str(e)}"
                )

    return {
        "code": code,
        "state": state,
        "res": res,
        "user_data": user_data,
    }
