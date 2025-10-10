from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import Response
from jose import jwt
from passlib.context import CryptContext

# import bcrypt
from pydantic import EmailStr

from backend.core.config import settings
from backend.core.logger import get_logger

logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Захэшировать пароль."""
    # return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    return str(pwd_context.hash(password))


def verify_password(password: str, hashed_password: str | None) -> bool:
    """Проверить пароль."""
    if not hashed_password:
        return False
    # return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    return bool(pwd_context.verify(password, hashed_password))


def is_valid_email(email: str) -> bool:
    """Проверить валидность email."""
    try:
        # Используем валидацию Pydantic для проверки email
        EmailStr._validate(email)
        return True
    except Exception:
        return False


def create_access_token(user_id: int) -> str:
    """Создать access token."""
    return _create_access_token_with_data({"user_id": user_id})


def _create_access_token_with_data(data: dict[str, Any]) -> str:
    """
    Создать access token.

    Args:
        data: данные для включения в токен

    Returns:
        str: сгенерированный JWT токен
    """
    to_encode = data.copy()
    expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(ZoneInfo("UTC")) + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return str(encoded_jwt)


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """
    Установить cookies для аутентификации.

    Args:
        response: HTTP response объект
        access_token: access token
        refresh_token: refresh token
    """
    # Устанавливаем access token cookie
    response.set_cookie(
        settings.ACCESS_TOKEN_COOKIE_NAME,
        access_token,
        httponly=True,
        samesite="none",
        secure=True,
    )

    # Устанавливаем refresh token cookie
    response.set_cookie(
        settings.REFRESH_TOKEN_COOKIE_NAME,
        refresh_token,
        httponly=True,
        samesite="none",
        secure=True,
        # path="/auth/refresh",
    )

    logger.info("Auth cookies set", extra={"access_token_set": True, "refresh_token_set": True})


def delete_auth_cookies(response: Response) -> None:
    """
    Удалить cookies для аутентификации.

    Args:
        response: HTTP response объект
    """
    # Удаляем access token cookie
    response.delete_cookie(settings.ACCESS_TOKEN_COOKIE_NAME)
    response.delete_cookie(settings.REFRESH_TOKEN_COOKIE_NAME)

    logger.info("Auth cookies deleted", extra={"access_token_deleted": True, "refresh_token_deleted": True})


if __name__ == "__main__":
    print(get_password_hash("123456"))
    print(verify_password("123456", get_password_hash("123456")))
