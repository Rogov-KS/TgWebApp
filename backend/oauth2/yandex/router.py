from typing import Annotated
from fastapi import APIRouter, Body
from fastapi.responses import RedirectResponse

import aiohttp
# import jwt
from jose import jwt

# from state_storage import state_storage
from backend.oauth2.yandex.utils import generate_yandex_oauth_redirect_uri
# from backend.core.config import settings

router = APIRouter(
    prefix="/yandex",
    tags=["OAuth2/Yandex"],
)


@router.get("/url")
def get_yandex_oauth_redirect_uri():
    uri = generate_yandex_oauth_redirect_uri()
    return uri
