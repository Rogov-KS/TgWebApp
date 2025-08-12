from fastapi import APIRouter, Depends, Response, Request
from pydantic import ValidationError

from backend.core.config import settings
from backend.core.dependecies import get_current_user
from backend.core.exception import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    InvalidOAuth2TokenException,
    InvalidEmailException,
)
from backend.dao.user import UserDAO
from backend.core.logger import get_logger
from backend.schemas.user import User, UserAuth, UserLogin
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
async def register(user_data: UserAuth) -> User:
    logger.info("Registering user: %s", user_data)

    if not is_valid_email(user_data.email):
        logger.info("Invalid email: %s", user_data.email)
        raise InvalidEmailException

    if user_data.username:
        existing_user = await UserDAO.get_one_or_none(username=user_data.username)
    else:
        existing_user = await UserDAO.get_one_or_none(email=user_data.email)

    if existing_user:
        logger.info(
            "User with email or username already exists: %s",
            user_data.email or user_data.username
        )
        raise UserAlreadyExistsException

    hashed_password = get_password_hash(user_data.password)

    logger.info("Creating user: %s", user_data)

    try:
        user = await UserDAO.create(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
        )
    except Exception as e:
        logger.error("Error creating user: %s", e)
        raise e

    logger.info("User created: %s", user)

    try:
        model_user = User.model_validate(user)
    except ValidationError as e:
        logger.error("Validation error: %s", e)
        await UserDAO.delete(id=user.id)
        raise e

    # Отправляем приветственное письмо асинхронно
    if user_data.email:
        logger.info("Try to send welcome email to %s", user_data.email)
        await send_welcome_email_task(
            user_email=user_data.email,
            username=user_data.username or user_data.email
        )

    return model_user


@router.post("/login")
async def login(response: Response, user_data: UserLogin) -> dict[str, str]:
    logger.info("Logging in user: %s", user_data)
    user = await authenticate_user(
        user_data.username_or_email, user_data.password
    )
    if not user:
        logger.info("Invalid credentials: %s", user_data)
        raise InvalidCredentialsException

    access_token, refresh_token = await set_tokens_to_cookies(response, user)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh")
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
        "New access token and refresh token created for user: %s", user.id
    )

    access_token, refresh_token = await set_tokens_to_cookies(response, user)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(
    response: Response, user: User = Depends(get_current_user)
) -> dict[str, str]:
    logger.info("Logging out user: %s", user.id)

    # Отзываем все refresh токены пользователя
    await revoke_user_refresh_tokens(user.id)

    # Удаляем cookies
    response.delete_cookie(settings.ACCESS_TOKEN_COOKIE_NAME)
    response.delete_cookie(settings.REFRESH_TOKEN_COOKIE_NAME)

    return {"message": "Logged out"}


@router.get("/me")
async def me(user: User = Depends(get_current_user)) -> User:
    logger.info("Getting user: %s", user)
    return user


@router.get("/hello_world")
async def hello_world() -> str:
    logger.info("Calling func 'hello world'")
    return "hello world"
