"""Интерфейсы для компонентов авторизации."""

from typing import Protocol

from fastapi import Request, Response

from backend.entities.assemblers.schemas import (
    SUser,
    SUserAuth,
    SUserLogin,
)


class IAuthService(Protocol):
    """Интерфейс для сервиса авторизации."""

    async def authenticate_user(
        self, username_or_email: str, password: str
    ) -> SUser | None:
        """Аутентифицировать пользователя."""

    async def authenticate_admin_user(
        self, username_or_email: str, password: str
    ) -> SUser | None:
        """Аутентифицировать администратора."""

    async def register_user(self, user_data: SUserAuth) -> SUser:
        """Зарегистрировать нового пользователя."""

    async def login_user(
        self, user_data: SUserLogin, response: Response
    ) -> dict[str, str]:
        """Выполнить вход пользователя."""

    async def refresh_tokens(
        self, request: Request, response: Response
    ) -> dict[str, str]:
        """Обновить токены."""

    async def logout_user(
        self, user: SUser, response: Response
    ) -> dict[str, str]:
        """Выполнить выход пользователя."""
