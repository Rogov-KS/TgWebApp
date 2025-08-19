"""Интерфейсы для компонентов OAuth2."""

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Protocol

from backend.ows.auth.models import OAuth2Token
from backend.ows.auth.schemas import CloudFile, OAuth2TokenData, OAuth2UserData


class IOAuth2TokenDAO(Protocol):
    """Интерфейс для DAO OAuth2 токенов."""

    async def get_all(self, **filter_by: Any) -> List[OAuth2Token]:
        """Получить все записи OAuth2 токенов."""

    async def get_one_or_none(self, **filter_by: Any) -> OAuth2Token | None:
        """Получить OAuth2 токен по фильтру или None."""

    async def create(self, **data: Any) -> OAuth2Token | None:
        """Создать новый OAuth2 токен."""

    async def delete(self, **filter_by: Any) -> bool:
        """Удалить OAuth2 токен."""

    async def update(
        self,
        filters: dict[str, Any],
        update_data: dict[str, Any],
    ) -> OAuth2Token | None:
        """Обновить OAuth2 токен."""


class IOAuth2Service(ABC):
    """Абстрактный интерфейс для OAuth2 провайдеров."""

    @property
    @abstractmethod
    def client_id(self) -> str:
        """Client ID провайдера."""

    @property
    @abstractmethod
    def client_secret(self) -> str:
        """Client Secret провайдера."""

    @property
    @abstractmethod
    def redirect_uri(self) -> str:
        """URI для перенаправления после авторизации."""

    @property
    @abstractmethod
    def authorization_url(self) -> str:
        """URL для авторизации пользователя."""

    @property
    @abstractmethod
    def token_url(self) -> str:
        """URL для получения токенов."""

    @property
    @abstractmethod
    def user_info_url(self) -> str:
        """URL для получения информации о пользователе."""

    @abstractmethod
    def get_authorization_params(self, state: str) -> dict[str, str]:
        """Параметры для URL авторизации."""

    @abstractmethod
    def get_token_params(self, code: str) -> dict[str, str]:
        """Параметры для запроса токенов."""

    @abstractmethod
    async def parse_user_data(
        self, raw_data: dict[str, Any]
    ) -> OAuth2UserData:
        """Парсинг данных пользователя из ответа провайдера."""

    @abstractmethod
    async def get_cloud_files(
        self, access_token: str
    ) -> List[CloudFile]:
        """Получение списка файлов из облачного хранилища провайдера."""

    @abstractmethod
    async def exchange_code_for_tokens(self, code: str) -> OAuth2TokenData:
        """Обмен authorization code на токены."""

    @abstractmethod
    async def get_user_data(self, access_token: str) -> Optional[OAuth2UserData]:
        """Получение данных пользователя через API провайдера."""

    @abstractmethod
    async def get_oauth2_user_data(
        self, code: str, state: str
    ) -> Optional[OAuth2UserData]:
        """Полный процесс аутентификации."""

    @abstractmethod
    async def authenticate_by_user_data(
        self, user_data: Optional[OAuth2UserData], response: Any
    ) -> dict[str, str]:
        """Аутентификация пользователя."""
