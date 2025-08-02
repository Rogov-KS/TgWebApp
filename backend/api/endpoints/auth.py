from fastapi import APIRouter, Depends, Response

from backend.core.config import settings
from backend.core.dependecies import get_current_user
from backend.core.exception import (
    InvalidTelegramIdOrPasswordException,
    UserAlreadyExistsException,
)
from backend.dao.user import UserDAO
from backend.logger import get_logger
from backend.schemas.user import User, UserAuth
from backend.utils.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
)

logger = get_logger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/register")
async def register(user_data: UserAuth) -> User | None:
    logger.info("Registering user: %s", user_data)
    existing_user = await UserDAO.get_one_or_none(telegram_id=user_data.telegram_id)
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

    return user


@router.post("/login")
async def login(response: Response, user_data: UserAuth) -> dict[str, str]:
    logger.info("Logging in user: %s", user_data)
    user = await authenticate_user(user_data.telegram_id, user_data.password)
    if not user:
        logger.info("Invalid credentials: %s", user_data)
        raise InvalidTelegramIdOrPasswordException

    access_token = create_access_token(data={"sub": str(user.telegram_id)})
    response.set_cookie(
        settings.AUTH_COOKIE_NAME,
        access_token,
        httponly=True,
        # samesite="strict",
        samesite="none",
        secure=True,

    )
    logger.info("Access token: %s", access_token)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    logger.info("Logging out user")
    response.delete_cookie(settings.AUTH_COOKIE_NAME)
    return {"message": "Logged out"}


@router.get("/me")
async def me(user: User = Depends(get_current_user)) -> User:
    logger.info("Getting user: %s", user)
    return user


@router.get("/hello_world")
async def hello_world() -> str:
    logger.info("Calling func 'hello world'")
    return "hello world"
