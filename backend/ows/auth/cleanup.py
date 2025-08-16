import asyncio

from backend.core.logger import get_logger
from backend.ows.auth.state_storage import state_storage

logger = get_logger(__name__)


async def cleanup_oauth_data() -> None:
    """Периодическая очистка OAuth данных"""
    while True:
        try:
            # Очищаем истекшие state
            state_storage.cleanup_expired_states()
            logger.debug("OAuth data cleanup completed")

        except Exception as e:
            logger.error("Error during OAuth cleanup", exc_info=True)

        # Очищаем каждые 5 минут
        await asyncio.sleep(300)


def start_cleanup_task() -> None:
    """Запускает задачу очистки"""
    asyncio.create_task(cleanup_oauth_data())
