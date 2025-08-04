from typing import Annotated
from fastapi import APIRouter, Body
from fastapi.responses import RedirectResponse

import aiohttp
# import jwt
from jose import jwt

# from state_storage import state_storage
from backend.oauth2.google.utils import generate_google_oauth_redirect_uri
from backend.core.config import settings

router = APIRouter(
    prefix="/google",
    tags=["OAuth2/Google"],
)


@router.get("/url")
def get_google_oauth_redirect_uri():
    uri = generate_google_oauth_redirect_uri()
    return uri
    return RedirectResponse(url=uri, status_code=302)


@router.post("/callback")
async def handle_code(
    code: str,
    state: str,
    # code: Annotated[str, Body()],
    # state: Annotated[str, Body()],
):
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
                "client_id": settings.OATH_GOOGLE_WEB_CLIENT1_ID,
                "client_secret": settings.OATH_GOOGLE_WEB_CLIENT1_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
                "code": code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            ssl=False,
        ) as response:
            res = await response.json()
            print(f"{res=}")
    #         id_token = res["id_token"]
    #         access_token = res["access_token"]
    #         user_data = jwt.decode(
    #             id_token,
    #             key="",
    #             algorithms=["RS256"],
    #             options={"verify_signature": False},
    #         )

    # async with aiohttp.ClientSession() as session:
    #     async with session.get(
    #         url="https://www.googleapis.com/drive/v3/files",
    #         headers={
    #             "Authorization": f"Bearer {access_token}"
    #         },
    #         ssl=False,
    #     ) as response:
    #         res = await response.json()
    #         print(f"{res=}")
    #         files = [item["name"] for item in res["files"]]

    return {
        "res": res,
        # "user": user_data,
        # "files": files,
    }
