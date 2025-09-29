from typing import Annotated

from fastapi import Depends, Request, Response
from pydantic import ValidationError

from backend.core.exception import (
    IncorrectTokenFormatException,
    InvalidCredentialsException,
    InvalidEmailException,
    UserAlreadyExistsException,
    InvalidOAuth2TokenException,
)
from backend.core.logger import get_logger
from backend.entities.auth.utils import (
    verify_password,
    get_password_hash,
    is_valid_email,
    create_access_token,
    set_auth_cookies,
    delete_auth_cookies,
)
from backend.entities.assemblers.schemas import (
    SUserAuth, SUserLogin, SUser, SUserRegister
)
from backend.entities.refresh_token.service import (
    RefreshTokenServiceDep,
)
from backend.entities.refresh_token.service import RefreshTokenService
from backend.entities.user.service import UserService, UserServiceDep
from backend.core.config import settings


logger = get_logger(__name__)


class AuthService:
    """Сервисный слой для аутентификации и управления пользователями."""

    def __init__(
        self,
        user_service: UserService,
        refresh_service: RefreshTokenService,
    ):
        self.user_service = user_service
        self.refresh_service = refresh_service

    async def authenticate_user(
        self,
        username_or_email: str,
        password: str
    ) -> SUser | None:
        """
        Аутентификация пользователя по username или email.

        Args:
            username_or_email: username или email пользователя
            password: пароль пользователя

        Returns:
            SUser | None: пользователь или None, если
                              аутентификация не удалась
        """

        user = None

        # Проверяем, является ли введенная строка email
        if is_valid_email(username_or_email):
            # Если это email, ищем пользователя по email
            user = await self.user_service.get_user_by(email=username_or_email)
        else:
            # Если это не email, ищем по username
            user = await self.user_service.get_user_by(
                username=username_or_email
            )

        if not user or not verify_password(password, user.hashed_password):
            return None

        try:
            schema_user = SUser.model_validate(user)
        except ValidationError as err:
            raise IncorrectTokenFormatException from err

        return schema_user

    async def authenticate_admin_user(
        self,
        username_or_email: str,
        password: str
    ) -> SUser | None:
        """
        Аутентификация администратора по username или email.

        Args:
            username_or_email: username или email пользователя
            password: пароль пользователя

        Returns:
            SUser | None: пользователь-админ или None, если
                              аутентификация не удалась или пользователь
                              не является администратором
        """
        user = await self.authenticate_user(username_or_email, password)
        if not user or not user.is_admin:
            return None
        return user

    async def register_user(self, user_data: SUserAuth) -> SUser:
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
        existing_user = await self.user_service.get_user_by(
            email=user_data.email
        )
        if existing_user:
            logger.info(
                "User already exists", extra={"email": user_data.email}
            )
            raise UserAlreadyExistsException

        # Проверяем, существует ли пользователь с таким username
        existing_user = await self.user_service.get_user_by(
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
        user_reg_data = SUserRegister(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
        )
        # Создаем пользователя
        try:
            schema_user = await self.user_service.create_user(
                user_data=user_reg_data
            )
            if not schema_user:
                logger.error("Failed to create user - returned None")
                raise UserAlreadyExistsException
        except Exception as e:
            logger.exception("Error creating user", exc_info=True)
            raise UserAlreadyExistsException from e

        logger.info(
            "User registered successfully", extra={"user_id": schema_user.id}
        )
        return schema_user

    async def login_user(
        self,
        user_data: SUserLogin,
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
        logger.info(
            "Logging in user", extra={"user_data": user_data.model_dump()}
        )
        user_schema = await self.authenticate_user(
            user_data.username_or_email, user_data.password
        )
        if not user_schema:
            logger.info(
                "Invalid credentials",
                extra={"user_data": user_data.model_dump()}
            )
            raise InvalidCredentialsException

        # Получаем модель пользователя для set_tokens_to_cookies
        schema_user = await self.user_service.get_user_by(id=user_schema.id)
        if not schema_user:
            raise InvalidCredentialsException

        access_token = create_access_token(schema_user.id)
        refresh_token = await self.refresh_service.create_refresh_token(
            schema_user.id
        )

        set_auth_cookies(
            response=response,
            access_token=access_token,
            refresh_token=refresh_token,
        )

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

        access_token = create_access_token(user.id)
        refresh_token = await self.refresh_service.create_refresh_token(
            user.id
        )

        # Удаляем cookies
        delete_auth_cookies(response)

        # Устанавливаем новые cookies
        set_auth_cookies(
            response=response,
            access_token=access_token,
            refresh_token=refresh_token,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def logout_user(
        self, user: SUser, response: Response
    ) -> dict[str, str]:
        """
        Выход пользователя из системы.

        Args:
            user: текущий пользователь
            response: HTTP response объект

        Returns:
            dict: сообщение об успешном выходе
        """

        logger.info("Logging out user", extra={"user_id": user.id})

        # Отзываем все refresh токены пользователя
        await self.refresh_service.revoke_all_user_tokens(user.id)

        # Удаляем cookies
        delete_auth_cookies(response)

        logger.info("User logged out successfully", extra={"user_id": user.id})
        return {"message": "Successfully logged out"}


def get_auth_service(
    user_service: UserServiceDep,
    refresh_service: RefreshTokenServiceDep
) -> AuthService:
    """Dependency для получения AuthService."""
    return AuthService(user_service, refresh_service)


# Тип для использования в роутерах
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
