import secrets
from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext
from pydantic import EmailStr

from backend.core.config import settings
from backend.dao.oauth2_token import Oauth2TokenDAO
from backend.dao.user import UserDAO
from backend.models.user import User
from backend.logger import get_logger


logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return str(pwd_context.hash(password))


def verify_password(password: str, hashed_password: str) -> bool:
    return bool(pwd_context.verify(password, hashed_password))


def is_valid_email(email: str) -> bool:
    """Проверяет, является ли строка валидным email адресом."""
    logger.info("Validating email: %s", email)
    try:
        EmailStr._validate(email)
        return True
    except Exception:
        return False


async def authenticate_user(
    username_or_email: str, password: str
) -> User | None:
    """Аутентификация пользователя по username или email."""
    user = None

    # Сначала проверяем, является ли введенная строка email
    if is_valid_email(username_or_email):
        # Если это email, ищем пользователя по email
        user = await UserDAO.get_one_or_none(
            email=username_or_email
        )
    else:
        # Если это не email, ищем по username
        user = await UserDAO.get_one_or_none(
            username=username_or_email
        )

    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return str(encoded_jwt)


def create_refresh_token(user_id: int) -> tuple[str, datetime]:
    """Создать refresh token для пользователя."""
    # Генерируем случайный токен
    token = secrets.token_urlsafe(32)

    # Вычисляем время истечения
    expire = datetime.utcnow() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    return token, expire


async def verify_refresh_token(token: str) -> User | None:
    """Проверить refresh token и вернуть пользователя."""
    refresh_token = await Oauth2TokenDAO.get_by_token(token)

    if not refresh_token:
        return None

    # Проверяем, что токен активен и не истек
    if (not refresh_token.is_active or
            refresh_token.expires_at is None or
            refresh_token.expires_at <= datetime.utcnow()):
        return None

    # Получаем пользователя
    user = await UserDAO.get_one_or_none(id=refresh_token.user_id)
    return user


async def revoke_refresh_token(token: str) -> None:
    """Отозвать refresh token."""
    await Oauth2TokenDAO.revoke_by_token(token)


async def revoke_user_refresh_tokens(user_id: int) -> None:
    """Отозвать все refresh токены пользователя."""
    await Oauth2TokenDAO.revoke_all_by_user_id(user_id)


async def create_user_refresh_token(user_id: int) -> str:
    """Создать refresh token для пользователя с ограничением количества."""
    # Проверяем количество активных токенов
    active_count = await Oauth2TokenDAO.count_active_by_user_id(user_id)

    if active_count >= settings.MAX_REFRESH_TOKENS_PER_USER:
        # Удаляем самый старый токен
        active_tokens = await Oauth2TokenDAO.get_active_by_user_id(user_id)
        if active_tokens:
            oldest_token = min(active_tokens, key=lambda t: t.created_at)
            if oldest_token.refresh_token:
                await Oauth2TokenDAO.revoke_by_token(
                    oldest_token.refresh_token
                )

    # Создаем новый токен
    token, expires_at = create_refresh_token(user_id)

    # Сохраняем в базу
    await Oauth2TokenDAO.create_refresh_token(
        user_id=user_id,
        refresh_token=token,
        expires_at=expires_at
    )

    return token
