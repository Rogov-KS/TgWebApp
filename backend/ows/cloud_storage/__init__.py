"""
OWS - Other Web Services
Интеграции с внешними сервисами через OAuth2
"""

from backend.ows.cloud_storage.base import CloudIntegration
from backend.ows.cloud_storage.google.drive import GoogleDriveIntegration
from backend.ows.cloud_storage.yandex.disk import YandexDiskIntegration
from backend.entities.assemblers.schemas import SCloudFile

__all__ = [
    "SCloudFile",
    "CloudIntegration",
    "GoogleDriveIntegration",
    "YandexDiskIntegration",
]
