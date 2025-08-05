from typing import Annotated, Any
from fastapi import APIRouter, Body
from fastapi.responses import RedirectResponse

import aiohttp
from jose import jwt

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


@router.post("/callback")
async def handle_code(
    code: str,
    state: str,
    # code: Annotated[str, Body()],
    # state: Annotated[str, Body()],
) -> dict[str, Any]:
    '''
    Handle Yandex OAuth callback

    Args:
        code: Authorization code
        state: State
    '''
    logger.info("handle_code into %s %s", code, state)
    # if state not in state_storage:
    #     raise
    # else:
    #     print("Стейт корректный")
    yandex_token_url = "https://oauth.yandex.ru/"
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
            print(f"{res=}")
            id_token = res["id_token"]
            access_token = res["access_token"]
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
            print(f"{res2=}")
            files = [item["name"] for item in res2["files"]]

    return {
        "user": user_data,
        "files": files,
    }
