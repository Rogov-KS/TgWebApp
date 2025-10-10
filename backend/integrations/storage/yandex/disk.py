"""Yandex.Disk интеграция"""

import aiohttp

from backend.core.logger import get_logger
from backend.entities.assemblers.schemas import SCloudFile
from backend.integrations.storage.base import CloudIntegration

logger = get_logger(__name__)


class YandexDiskIntegration(CloudIntegration):
    """Интеграция с Яндекс.Диском"""

    def __init__(self) -> None:
        super().__init__("yandex_disk")
        self.api_base_url = "https://cloud-api.yandex.net/v1/disk"

    async def get_files(self, access_token: str) -> list[SCloudFile]:
        """Получение файлов из Яндекс.Диска"""
        disk_url = f"{self.api_base_url}/resources/files"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=disk_url,
                headers={
                    "Authorization": f"OAuth {access_token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                ssl=False,
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.exception(
                        "Failed to get Yandex.Disk files",
                        exc_info=True,
                        extra={"status": response.status, "response": error_text},
                    )
                    return []

                data = await response.json()
                items = data.get("items", [])

                return [
                    SCloudFile(
                        name=item.get("name", ""),
                        id=item.get("resource_id"),
                        size=item.get("size"),
                        mime_type=item.get("mime_type"),
                        modified_time=item.get("modified"),
                        download_url=item.get("file"),
                    )
                    for item in items
                    if item.get("type") == "file"  # Только файлы, не папки
                ]
