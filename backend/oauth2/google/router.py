from typing import Annotated, Any
from fastapi import APIRouter, Body
from fastapi.responses import RedirectResponse

import aiohttp
import jwt

# from state_storage import state_storage
from backend.oauth2.google.utils import generate_google_oauth_redirect_uri
from backend.core.config import settings
from backend.logger import get_logger


router = APIRouter(
    prefix="/google",
    tags=["OAuth2/Google"],
)

logger = get_logger(__name__)


@router.get("/url")
def get_google_oauth_redirect_uri() -> RedirectResponse:
    '''
    Get Google OAuth redirect URI

    Returns:
        RedirectResponse: Redirect to Google OAuth redirect URI
    '''
    uri = generate_google_oauth_redirect_uri()
    logger.info("get_google_oauth_redirect_uri into %s", uri)
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
    logger.info("handle_code into %s %s", code, state)
    # if state not in state_storage:
    #     raise
    # else:
    #     print("Стейт корректный")
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
            print(f"{res=}")
            id_token = res.get("id_token")
            access_token = res.get("access_token")
            refresh_token = res.get("refresh_token")
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
