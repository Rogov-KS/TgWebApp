from datetime import UTC, datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from backend.core.config import settings
from backend.dao.user import UserDAO
from backend.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return str(pwd_context.hash(password))


def verify_password(password: str, hashed_password: str) -> bool:
    return bool(pwd_context.verify(password, hashed_password))


async def authenticate_user(telegram_id: int, password: str) -> User | None:
    user = await UserDAO.get_one_or_none(telegram_id=telegram_id)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return str(encoded_jwt)
