from datetime import datetime, timezone

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
from backend.entities.user.dao import UserDAO
from backend.entities.user.schemas import User as UserSchema
from backend.core.logger import get_logger
from backend.entities.user.models import User
from pydantic import ValidationError


logger = get_logger(__name__)


def get_token(request: Request) -> str:
    token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)
    if not token:
        raise TokenAbsentException
    return str(token)


async def get_current_user(token: str = Depends(get_token)) -> UserSchema:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload is None:
            raise NotAuthenticatedException
    except JWTError as err:
        raise IncorrectTokenFormatException from err

    expire = payload.get("exp")
    logger.info("Token expire check", extra={"expire": expire})
    if not expire or (int(expire) < int(datetime.now(timezone.utc).timestamp())):
        raise TokenExpiredException

    user_id = payload.get("sub")
    if not user_id:
        raise UserNotFoundException

    user = await UserDAO.get_one_or_none(id=int(user_id))
    if not user:
        raise UserNotFoundException

    try:
        schema_user = UserSchema.model_validate(user)
    except ValidationError as err:
        raise IncorrectTokenFormatException from err

    return schema_user


async def get_current_admin_user(user: UserSchema = Depends(get_current_user)) -> UserSchema:
    if not user or not user.is_admin:
        raise ForbiddenException
    return user


async def get_current_admin_user_by_token(token: str = Depends(get_token)) -> UserSchema:
    user = await get_current_user(token)
    if not user or not user.is_admin:
        raise ForbiddenException
    return user
