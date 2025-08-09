from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import aiohttp
from fastapi import HTTPException

from backend.logger import get_logger
from backend.schemas import CloudFile, OAuth2TokenData, OAuth2UserData

logger = get_logger(__name__)


class OAuth2Provider(ABC):
    """Абстрактный базовый класс для OAuth2 провайдеров"""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self._processing_requests: dict[str, bool] = {}

    @property
    @abstractmethod
    def client_id(self) -> str:
        """Client ID провайдера"""

    @property
    @abstractmethod
    def client_secret(self) -> str:
        """Client Secret провайдера"""

    @property
    @abstractmethod
    def redirect_uri(self) -> str:
        """URI для перенаправления после авторизации"""

    @property
    @abstractmethod
    def authorization_url(self) -> str:
        """URL для авторизации пользователя"""

    @property
    @abstractmethod
    def token_url(self) -> str:
        """URL для получения токенов"""

    @property
    @abstractmethod
    def user_info_url(self) -> str:
        """URL для получения информации о пользователе"""

    @abstractmethod
    def get_authorization_params(self, state: str) -> dict[str, str]:
        """Параметры для URL авторизации"""

    @abstractmethod
    def get_token_params(self, code: str) -> dict[str, str]:
        """Параметры для запроса токенов"""

    @abstractmethod
    def parse_user_data(self, raw_data: dict[str, Any]) -> OAuth2UserData:
        """Парсинг данных пользователя из ответа провайдера"""

    @abstractmethod
    async def get_cloud_files(self, access_token: str) -> list[CloudFile]:
        """Получение списка файлов из облачного хранилища провайдера"""

    @contextmanager
    def _single_processing_request(self, request_key: str) -> Iterator[None]:
        """
        Гарантирует, что запрос с тем же ключом
        обрабатывается только один раз.
        """
        if request_key in self._processing_requests:
            logger.warning("Request already being processed: %s", request_key)
            raise HTTPException(
                status_code=429,
                detail="Request is already being processed",
            )
        self._processing_requests[request_key] = True
        try:
            yield
        finally:
            self._processing_requests.pop(request_key, None)

    async def exchange_code_for_tokens(self, code: str) -> OAuth2TokenData:
        """Обмен authorization code на токены"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.token_url,
                data=self.get_token_params(code),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                ssl=False,
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        "Failed to get access token from %s. "
                        "Status: %d, Response: %s",
                        self.provider_name,
                        response.status,
                        error_text,
                    )
                    raise HTTPException(
                        status_code=response.status,
                        detail=(
                            f"Failed to get access token from "
                            f"{self.provider_name}: {error_text}"
                        ),
                    )

                data = await response.json()
                return OAuth2TokenData(
                    access_token=data.get("access_token", ""),
                    refresh_token=data.get("refresh_token"),
                    token_type=data.get("token_type", "Bearer"),
                    expires_in=data.get("expires_in"),
                    scope=data.get("scope"),
                    id_token=data.get("id_token"),
                    raw_data=data,
                )

    async def get_user_data(self, access_token: str) -> OAuth2UserData:
        """Получение данных пользователя через API провайдера"""
        if not self.user_info_url:
            raise NotImplementedError(
                f"User info URL not implemented for {self.provider_name}"
            )

        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {access_token}"}

            # Для некоторых провайдеров (например, Yandex) нужен другой
            # формат заголовка
            if self.provider_name == "yandex":
                headers["Authorization"] = f"OAuth {access_token}"
                headers["Content-Type"] = "application/json"

            async with session.get(
                url=self.user_info_url,
                headers=headers,
                ssl=False,
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        "Failed to get user data from %s. "
                        "Status: %d, Response: %s",
                        self.provider_name,
                        response.status,
                        error_text,
                    )
                    raise HTTPException(
                        status_code=response.status,
                        detail=(
                            f"Failed to get user data from "
                            f"{self.provider_name}: {error_text}"
                        ),
                    )

                data = await response.json()
                return self.parse_user_data(data)

    async def authenticate(
        self, code: str, state: str
    ) -> tuple[OAuth2UserData, list[CloudFile]]:
        """Полный процесс аутентификации"""
        from backend.oauth2.state_storage import state_storage

        request_key = f"{state}_{code}"
        with self._single_processing_request(request_key):
            # Валидируем state
            state_storage.validate_state_or_raise(state, self.provider_name)

            # Получаем токены
            token_data = await self.exchange_code_for_tokens(code)

            # Получаем данные пользователя
            if self.provider_name == "google" and token_data.id_token:
                # Для Google используем id_token
                user_data = self.parse_user_data(token_data.raw_data or {})
            else:
                # Для других провайдеров делаем запрос к API
                user_data = await self.get_user_data(token_data.access_token)

            # Получаем файлы из облачного хранилища
            try:
                cloud_files = await self.get_cloud_files(
                    token_data.access_token
                )
            except Exception as e:
                logger.warning(
                    "Failed to get cloud files from %s: %s",
                    self.provider_name,
                    e,
                )
                cloud_files = []

            return user_data, cloud_files
