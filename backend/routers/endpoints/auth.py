from fastapi import APIRouter, Depends, Response, Request
from pydantic import ValidationError
from fastapi_versioning import version

from backend.core.config import settings
from backend.core.dependecies import get_current_user, get_current_admin_user
from backend.core.exception import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    InvalidOAuth2TokenException,
    InvalidEmailException,
)
from backend.entities.user.dao import UserDAO
from backend.core.logger import get_logger
from backend.entities.user.schemas import User, UserAuth, UserLogin
from backend.utils.auth import (
    authenticate_user,
    get_password_hash,
    verify_refresh_token,
    revoke_user_refresh_tokens,
    revoke_refresh_token,
    is_valid_email,
    set_tokens_to_cookies,
)
from backend.celery_app.tasks.email import send_welcome_email_task

logger = get_logger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/register")
@version(1)
async def register(user_data: UserAuth) -> User:
    logger.info(
        "Registering user",
        extra={"user_data": user_data.model_dump()}
    )

    if not is_valid_email(user_data.email):
        logger.info("Invalid email", extra={"email": user_data.email})
        raise InvalidEmailException

    if user_data.username:
        existing_user = await UserDAO.get_one_or_none(username=user_data.username)
    else:
        existing_user = await UserDAO.get_one_or_none(email=user_data.email)

    if existing_user:
        logger.info(
            "User with email or username already exists",
            extra={
                "email": user_data.email,
                "username": user_data.username
            }
        )
        raise UserAlreadyExistsException

    hashed_password = get_password_hash(user_data.password)

    logger.info("Creating user", extra={"user_data": user_data.model_dump()})

    try:
        user = await UserDAO.create(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
        )
    except Exception as e:
        logger.error("Error creating user", exc_info=True)
        raise e

    logger.info(
        "User created",
        extra={"user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_admin": user.is_admin,
            "is_bot": user.is_bot,
            "is_active": user.is_active,
            "max_score": user.max_score,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": (
                user.updated_at.isoformat() if user.updated_at else None
            )
        } if user else None}
    )

    try:
        model_user = User.model_validate(user)
    except ValidationError as e:
        logger.error("Validation error", exc_info=True)
        await UserDAO.delete(id=user.id)
        raise e

    # Отправляем приветственное письмо асинхронно
    if user_data.email:
        logger.info("Try to send welcome email", extra={"email": user_data.email})
        await send_welcome_email_task(
            user_email=user_data.email,
            username=user_data.username or user_data.email
        )

    return model_user


@router.post("/login")
@version(1)
async def login(response: Response, user_data: UserLogin) -> dict[str, str]:
    logger.info("Logging in user", extra={"user_data": user_data.model_dump()})
    user = await authenticate_user(
        user_data.username_or_email, user_data.password
    )
    if not user:
        logger.info(
            "Invalid credentials",
            extra={"user_data": user_data.model_dump()}
        )
        raise InvalidCredentialsException

    access_token, refresh_token = await set_tokens_to_cookies(response, user)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh")
@version(1)
async def refresh(
    response: Response,
    request: Request
) -> dict[str, str]:
    """Обновить access token используя refresh token с ротацией
    refresh токена."""
    logger.info("Refreshing token")

    # Проверяем refresh token
    refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)
    if not refresh_token:
        logger.info("No refresh token found")
        raise InvalidOAuth2TokenException

    user = await verify_refresh_token(refresh_token)
    if not user:
        logger.info("Invalid refresh token")
        raise InvalidOAuth2TokenException

    # Отзываем старый refresh token
    await revoke_refresh_token(refresh_token)

    logger.info(
        "New access token and refresh token created for user",
        extra={"user_id": user.id}
    )

    access_token, refresh_token = await set_tokens_to_cookies(response, user)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
@version(1)
async def logout(
    response: Response, user: User = Depends(get_current_user)
) -> dict[str, str]:
    logger.info("Logging out user", extra={"user_id": user.id})

    # Отзываем все refresh токены пользователя
    await revoke_user_refresh_tokens(user.id)

    logger.info("Deleting cookies", extra={"cookies": {
        "access_token": settings.ACCESS_TOKEN_COOKIE_NAME,
        "refresh_token": settings.REFRESH_TOKEN_COOKIE_NAME
    }})
    # Удаляем cookies
    response.delete_cookie(settings.ACCESS_TOKEN_COOKIE_NAME)
    response.delete_cookie(settings.REFRESH_TOKEN_COOKIE_NAME)

    return {"message": "Logged out"}


@router.get("/me")
@version(1)
async def me(user: User = Depends(get_current_user)) -> User:
    logger.info("Getting user", extra={"user": user.model_dump()})
    return user


@router.get("/me_admin")
@version(1)
async def me_admin(user: User = Depends(get_current_admin_user)) -> User:
    logger.info("Getting user", extra={"user": user.model_dump()})
    return user
