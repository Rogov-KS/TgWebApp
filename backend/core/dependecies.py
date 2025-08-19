from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, Request
from jose import JWTError, jwt
from pydantic import ValidationError

from backend.core.config import settings
from backend.core.exception import (
    ForbiddenException,
    IncorrectTokenFormatException,
    NotAuthenticatedException,
    TokenAbsentException,
    TokenExpiredException,
    UserNotFoundException,
)
from backend.core.logger import get_logger
from backend.entities.user.dao import UserDAODep
from backend.entities.user.schemas import User as UserSchema

logger = get_logger(__name__)


def get_token(request: Request) -> str:
    token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)
    if not token:
        raise TokenAbsentException
    return str(token)


AccessTokenDep = Annotated[str, Depends(get_token)]


async def get_current_user(
    token: AccessTokenDep,
    user_dao: UserDAODep,
) -> UserSchema:
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
    if not expire or (int(expire) < int(datetime.now(UTC).timestamp())):
        raise TokenExpiredException

    user_id = payload.get("sub")
    if not user_id:
        raise UserNotFoundException

    user = await user_dao.get_one_or_none(id=int(user_id))
    if not user:
        raise UserNotFoundException

    try:
        schema_user = UserSchema.model_validate(user)
    except ValidationError as err:
        raise IncorrectTokenFormatException from err

    return schema_user

CurrentUserDep = Annotated[UserSchema, Depends(get_current_user)]


async def get_current_admin_user(
    user: CurrentUserDep,
) -> UserSchema:
    if not user or not user.is_admin:
        raise ForbiddenException
    return user

CurrentAdminUserDep = Annotated[UserSchema, Depends(get_current_admin_user)]


async def get_current_admin_user_by_token(
    token: AccessTokenDep,
    user_dao: UserDAODep,
) -> UserSchema:
    user = await get_current_user(token, user_dao)
    if not user or not user.is_admin:
        raise ForbiddenException
    return user

CurrentAdminUserByTokenDep = Annotated[UserSchema, Depends(get_current_admin_user_by_token)]