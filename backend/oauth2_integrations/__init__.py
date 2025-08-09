"""Интеграции с внешними сервисами через OAuth2"""

from .base import CloudFile, CloudIntegration
from .google.drive import GoogleDriveIntegration
from .yandex.disk import YandexDiskIntegration

__all__ = [
    "CloudFile",
    "CloudIntegration",
    "GoogleDriveIntegration",
    "YandexDiskIntegration"
]
