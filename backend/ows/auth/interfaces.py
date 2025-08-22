"""Интерфейсы для компонентов OAuth2."""

from backend.core.base_dao import IBaseDAO
from backend.ows.auth.models import OAuth2TokenDB


class IOAuth2TokenDAO(IBaseDAO[OAuth2TokenDB]):
    """Интерфейс для DAO OAuth2 токенов."""
    # Базовые методы уже определены в IBaseDAO
