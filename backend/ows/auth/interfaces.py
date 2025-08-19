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
