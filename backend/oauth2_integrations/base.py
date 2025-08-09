"""Базовые классы для интеграций с внешними сервисами через OAuth2"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class CloudFile:
    """Информация о файле в облачном хранилище"""

    name: str
    id: str | None = None
    size: int | None = None
    mime_type: str | None = None
    modified_time: str | None = None
    download_url: str | None = None


class CloudIntegration(ABC):
    """Абстрактный базовый класс для интеграций с облачными сервисами"""

    def __init__(self, service_name: str):
        self.service_name = service_name

    @abstractmethod
    async def get_files(self, access_token: str) -> List[CloudFile]:
        """Получение списка файлов из облачного хранилища"""
