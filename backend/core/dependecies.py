from datetime import datetime

from fastapi import Depends, Request
from jose import JWTError, jwt

from backend.core.config import settings
from backend.core.exception import (
    ForbiddenException,
    IncorrectTokenFormatException,
    NotAuthenticatedException,
    TokenAbsentException,
    TokenExpiredException,
    UserNotFoundException,
)
from backend.dao.user import UserDAO
from backend.logger import get_logger
from backend.models.user import User

logger = get_logger(__name__)


def get_token(request: Request) -> str:
    token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)
    if not token:
        raise TokenAbsentException
    return str(token)


async def get_current_user(token: str = Depends(get_token)) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload is None:
            raise NotAuthenticatedException
    except JWTError as err:
        raise IncorrectTokenFormatException from err

    expire = payload.get("exp")
    logger.info("expire: %s", expire)
    if not expire or (int(expire) < int(datetime.utcnow().timestamp())):
        raise TokenExpiredException

    telegram_id = payload.get("sub")
    if not telegram_id:
        raise UserNotFoundException

    user = await UserDAO.get_one_or_none(telegram_id=int(telegram_id))
    if not user:
        raise UserNotFoundException

    logger.info("user: %s", user)
    return user


async def get_current_admin_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise ForbiddenException
    return user
