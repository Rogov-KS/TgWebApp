"""Базовые классы для интеграций с внешними сервисами через OAuth2"""

from abc import ABC, abstractmethod
from typing import List

from backend.entities.assemblers.schemas import CloudFile


class CloudIntegration(ABC):
    """Абстрактный базовый класс для интеграций с облачными сервисами"""

    def __init__(self, service_name: str):
        self.service_name = service_name

    @abstractmethod
    async def get_files(self, access_token: str) -> List[CloudFile]:
        """Получение списка файлов из облачного хранилища"""
