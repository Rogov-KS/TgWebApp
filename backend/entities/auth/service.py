from typing import Annotated

from fastapi import Depends, Request, Response
from pydantic import ValidationError

from backend.core.exception import (
    IncorrectTokenFormatException,
    InvalidCredentialsException,
    InvalidEmailException,
    UserAlreadyExistsException,
)
from backend.core.logger import get_logger
from backend.entities.auth.utils import (
    verify_password,
    get_password_hash,
    is_valid_email,
)
from backend.entities.user.dao import UserDAO, UserDAODep
from backend.entities.user.schemas import User, UserAuth, UserLogin
from backend.entities.user.schemas import User as UserSchema
from backend.entities.refresh_token.service import (
    RefreshTokenService,
    RefreshTokenServiceDep,
)

logger = get_logger(__name__)


class AuthService:
    """Сервисный слой для аутентификации и управления пользователями."""

    def __init__(
        self,
        user_dao: UserDAO,
        refresh_service: RefreshTokenService,
    ):
        self.user_dao = user_dao
        self.refresh_service = refresh_service

    async def authenticate_user(
        self,
        username_or_email: str,
        password: str
    ) -> UserSchema | None:
        """
        Аутентификация пользователя по username или email.

        Args:
            username_or_email: username или email пользователя
            password: пароль пользователя

        Returns:
            UserSchema | None: пользователь или None, если
                              аутентификация не удалась
        """

        user = None

        # Проверяем, является ли введенная строка email
        if is_valid_email(username_or_email):
            # Если это email, ищем пользователя по email
            user = await self.user_dao.get_one_or_none(email=username_or_email)
        else:
            # Если это не email, ищем по username
            user = await self.user_dao.get_one_or_none(
                username=username_or_email
            )

        if not user or not verify_password(password, user.hashed_password):
            return None

        try:
            schema_user = UserSchema.model_validate(user)
        except ValidationError as err:
            raise IncorrectTokenFormatException from err

        return schema_user

    async def authenticate_admin_user(
        self, username_or_email: str, password: str
    ) -> UserSchema | None:
        """
        Аутентификация администратора по username или email.

        Args:
            username_or_email: username или email пользователя
            password: пароль пользователя

        Returns:
            UserSchema | None: пользователь-админ или None, если
                              аутентификация не удалась или пользователь
                              не является администратором
        """
        user = await self.authenticate_user(username_or_email, password)
        if not user or not user.is_admin:
            return None
        return user

    async def register_user(self, user_data: UserAuth) -> User:
        """
        Регистрация нового пользователя.

        Args:
            user_data: данные для регистрации

        Returns:
            User: созданный пользователь

        Raises:
            InvalidEmailException: если email невалидный
            UserAlreadyExistsException: если пользователь уже существует
        """
        logger.info(
            "Registering user", extra={"user_data": user_data.model_dump()}
        )

        # Проверяем валидность email
        if not is_valid_email(user_data.email):
            logger.info("Invalid email", extra={"email": user_data.email})
            raise InvalidEmailException

        # Проверяем, существует ли пользователь с таким email
        existing_user = await self.user_dao.get_one_or_none(
            email=user_data.email
        )
        if existing_user:
            logger.info(
                "User already exists", extra={"email": user_data.email}
            )
            raise UserAlreadyExistsException

        # Проверяем, существует ли пользователь с таким username
        existing_user = await self.user_dao.get_one_or_none(
            username=user_data.username
        )
        if existing_user:
            logger.info(
                "Username already exists",
                extra={"username": user_data.username}
            )
            raise UserAlreadyExistsException

        # Хешируем пароль
        hashed_password = get_password_hash(user_data.password)

        # Создаем пользователя
        try:
            model_user = await self.user_dao.create(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
            )
        except Exception as e:
            logger.exception("Error creating user", exc_info=True)
            raise UserAlreadyExistsException from e

        logger.info(
            "User registered successfully", extra={"user_id": model_user.id}
        )
        return model_user

    async def login_user(
        self,
        user_data: UserLogin,
        response: Response,
    ) -> dict[str, str]:
        """
        Вход пользователя в систему.

        Args:
            user_data: данные для входа
            response: HTTP response объект
            refresh_service: сервис для работы с refresh токенами

        Returns:
            dict: токены доступа

        Raises:
            InvalidCredentialsException: если учетные данные неверны
        """
        logger.info("Logging in user", extra={"user_data": user_data.model_dump()})
        user = await self.authenticate_user(
            user_data.username_or_email, user_data.password
        )
        if not user:
            logger.info(
                "Invalid credentials", extra={"user_data": user_data.model_dump()}
            )
            raise InvalidCredentialsException

        tokens = await self.refresh_service.set_tokens_to_cookies(
            response, user
        )
        access_token, refresh_token = tokens

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh_tokens(
        self,
        request: Request,
        response: Response,
    ) -> dict[str, str]:
        """
        Обновление токенов доступа.

        Args:
            request: HTTP request объект
            response: HTTP response объект
            refresh_service: сервис для работы с refresh токенами

        Returns:
            dict: новые токены доступа

        Raises:
            InvalidOAuth2TokenException: если токен невалидный
        """
        from backend.core.config import settings
        from backend.core.exception import InvalidOAuth2TokenException

        logger.info("Refreshing token")

        # Проверяем refresh token
        refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)
        if not refresh_token:
            logger.info("No refresh token found")
            raise InvalidOAuth2TokenException

        user = await self.refresh_service.verify_refresh_token(refresh_token)
        if not user:
            logger.info("Invalid refresh token")
            raise InvalidOAuth2TokenException

        # Отзываем старый refresh token
        await self.refresh_service.revoke_token(refresh_token)

        logger.info(
            "New access token and refresh token created for user",
            extra={"user_id": user.id},
        )

        tokens = await self.refresh_service.set_tokens_to_cookies(
            response, user
        )
        access_token, new_refresh_token = tokens

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    async def logout_user(
        self, user: User, response: Response
    ) -> dict[str, str]:
        """
        Выход пользователя из системы.

        Args:
            user: текущий пользователь
            response: HTTP response объект

        Returns:
            dict: сообщение об успешном выходе
        """
        from backend.core.config import settings

        logger.info("Logging out user", extra={"user_id": user.id})

        # Отзываем все refresh токены пользователя
        await self.refresh_service.revoke_all_user_tokens(user.id)

        # Удаляем cookies
        response.delete_cookie(settings.ACCESS_TOKEN_COOKIE_NAME)
        response.delete_cookie(settings.REFRESH_TOKEN_COOKIE_NAME)

        logger.info("User logged out successfully", extra={"user_id": user.id})
        return {"message": "Successfully logged out"}


def get_auth_service(
    user_dao: UserDAODep,
    refresh_service: RefreshTokenServiceDep
) -> AuthService:
    """Dependency для получения AuthService."""
    return AuthService(user_dao, refresh_service)


# Тип для использования в роутерах
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
