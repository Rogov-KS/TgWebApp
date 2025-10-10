"""
OWS - Other Web Services
Интеграции с внешними сервисами через OAuth2
"""

from backend.entities.assemblers.schemas import SCloudFile
from backend.integrations.storage.base import CloudIntegration
from backend.integrations.storage.google.drive import GoogleDriveIntegration
from backend.integrations.storage.yandex.disk import YandexDiskIntegration

__all__ = [
    "CloudIntegration",
    "GoogleDriveIntegration",
    "SCloudFile",
    "YandexDiskIntegration",
]
