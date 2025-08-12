"""Google Drive интеграция"""

import aiohttp
from typing import List

from backend.core.logger import get_logger
from backend.oauth2_integrations.base import CloudIntegration
from backend.schemas import CloudFile

logger = get_logger(__name__)


class GoogleDriveIntegration(CloudIntegration):
    """Интеграция с Google Drive"""

    def __init__(self) -> None:
        super().__init__("google_drive")
        self.api_base_url = "https://www.googleapis.com/drive/v3"

    async def get_files(self, access_token: str) -> List[CloudFile]:
        """Получение файлов из Google Drive"""
        drive_url = f"{self.api_base_url}/files"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=drive_url,
                headers={"Authorization": f"Bearer {access_token}"},
                params={
                    "fields": (
                        "files(id,name,size,mimeType,modifiedTime,webViewLink)"
                    ),
                    "pageSize": 100
                },
                ssl=False,
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(
                        "Failed to get Google Drive files. "
                        "Status: %d, Response: %s",
                        response.status, error_text
                    )
                    return []

                data = await response.json()
                files = data.get("files", [])

                return [
                    CloudFile(
                        name=file.get("name", ""),
                        id=file.get("id"),
                        size=(
                            int(file.get("size", 0))
                            if file.get("size") else None
                        ),
                        mime_type=file.get("mimeType"),
                        modified_time=file.get("modifiedTime"),
                        download_url=file.get("webViewLink"),
                    )
                    for file in files
                ]
