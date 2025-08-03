from fastapi import APIRouter, Depends, Response, Request

from backend.core.config import settings
from backend.core.dependecies import get_current_user
from backend.core.exception import (
    InvalidTelegramIdOrPasswordException,
    UserAlreadyExistsException,
    InvalidRefreshTokenException,
)
from backend.dao.user import UserDAO
from backend.logger import get_logger
from backend.schemas.user import User, UserAuth
from backend.utils.auth import (
    authenticate_user,
    create_access_token,
    create_user_refresh_token,
    get_password_hash,
    verify_refresh_token,
    revoke_user_refresh_tokens,
    revoke_refresh_token,
)

logger = get_logger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/register")
async def register(user_data: UserAuth) -> User:
    logger.info("Registering user: %s", user_data)
    existing_user = await UserDAO.get_one_or_none(
        telegram_id=user_data.telegram_id
    )
    if existing_user:
        logger.info("User already exists: %s", user_data)
        raise UserAlreadyExistsException

    logger.info("Creating user: %s", user_data)
    hashed_password = get_password_hash(user_data.password)
    logger.info("Hashed password: %s", hashed_password)

    user = await UserDAO.create(
        telegram_id=user_data.telegram_id,
        username=user_data.username,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
    )
    logger.info("User created: %s", user)

    return User.model_validate(user)


@router.post("/login")
async def login(response: Response, user_data: UserAuth) -> dict[str, str]:
    logger.info("Logging in user: %s", user_data)
    user = await authenticate_user(user_data.telegram_id, user_data.password)
    if not user:
        logger.info("Invalid credentials: %s", user_data)
        raise InvalidTelegramIdOrPasswordException

    # Создаем access token
    access_token = create_access_token(data={"sub": str(user.telegram_id)})

    # Создаем refresh token
    refresh_token = await create_user_refresh_token(user.id)

    # Устанавливаем cookies
    response.set_cookie(
        settings.ACCESS_TOKEN_COOKIE_NAME,
        access_token,
        httponly=True,
        samesite="none",
        secure=True,
    )
    response.set_cookie(
        settings.REFRESH_TOKEN_COOKIE_NAME,
        refresh_token,
        httponly=True,
        samesite="none",
        secure=True,
        path="/auth/refresh",
    )

    logger.info("Access token: %s", access_token)
    logger.info("Refresh token created for user: %s", user.id)

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
        raise InvalidRefreshTokenException

    user = await verify_refresh_token(refresh_token)
    if not user:
        logger.info("Invalid refresh token")
        raise InvalidRefreshTokenException

    # Отзываем старый refresh token
    await revoke_refresh_token(refresh_token)

    # Создаем новый access token
    access_token = create_access_token(data={"sub": str(user.telegram_id)})

    # Создаем новый refresh token (ротация)
    new_refresh_token = await create_user_refresh_token(user.id)

    # Обновляем cookies
    response.set_cookie(
        settings.ACCESS_TOKEN_COOKIE_NAME,
        access_token,
        httponly=True,
        samesite="none",
        secure=True,
    )
    response.set_cookie(
        settings.REFRESH_TOKEN_COOKIE_NAME,
        new_refresh_token,
        httponly=True,
        samesite="none",
        secure=True,
        path="/auth/refresh",
    )

    logger.info(
        "New access token and refresh token created for user: %s", user.id
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
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
