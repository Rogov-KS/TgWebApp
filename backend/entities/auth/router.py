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
from backend.entities.auth.utils import (
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
    logger.info("Registering user", extra={"user_data": user_data.model_dump()})

    # Проверяем валидность email
    if not is_valid_email(user_data.email):
        logger.info("Invalid email", extra={"email": user_data.email})
        raise InvalidEmailException

    # Проверяем, существует ли пользователь с таким email
    existing_user = await UserDAO.get_one_or_none(email=user_data.email)
    if existing_user:
        logger.info("User already exists", extra={"email": user_data.email})
        raise UserAlreadyExistsException

    # Проверяем, существует ли пользователь с таким username
    existing_user = await UserDAO.get_one_or_none(username=user_data.username)
    if existing_user:
        logger.info("Username already exists", extra={"username": user_data.username})
        raise UserAlreadyExistsException

    # Хешируем пароль
    hashed_password = get_password_hash(user_data.password)

    # Создаем пользователя
    try:
        model_user = await UserDAO.create(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
        )
    except Exception as e:
        logger.error("Error creating user", exc_info=True)
        raise UserAlreadyExistsException from e

    # Отправляем приветственное письмо
    if user_data.email:
        logger.info("Try to send welcome email", extra={"email": user_data.email})
        await send_welcome_email_task(
            user_email=user_data.email,
            username=user_data.username
        )

    logger.info("User registered successfully", extra={"user_id": model_user.id})
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
    """Выйти из системы."""
    logger.info("Logging out user", extra={"user_id": user.id})

    # Отзываем все refresh токены пользователя
    await revoke_user_refresh_tokens(user.id)

    # Удаляем cookies
    response.delete_cookie(settings.ACCESS_TOKEN_COOKIE_NAME)
    response.delete_cookie(settings.REFRESH_TOKEN_COOKIE_NAME)

    logger.info("User logged out successfully", extra={"user_id": user.id})
    return {"message": "Successfully logged out"}


@router.get("/me")
@version(1)
async def get_current_user_info(
    user: User = Depends(get_current_user)
) -> User:
    """Получить информацию о текущем пользователе."""
    return user


@router.get("/hello_world")
@version(1)
async def hello_world() -> dict[str, str]:
    """Тестовый эндпоинт."""
    return {"message": "Hello World from Auth!"}
