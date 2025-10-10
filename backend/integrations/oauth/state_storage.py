import asyncio
from datetime import UTC, datetime, timedelta
import secrets

from fastapi import HTTPException

from backend.core.logger import get_logger

logger = get_logger(__name__)


class StateStorage:
    """Хранилище для OAuth state параметров"""

    def __init__(self) -> None:
        self._states: dict[str, dict] = {}
        # Множество для отслеживания обрабатываемых states
        self._processing_states: set = set()

    def generate_state(self, provider: str) -> str:
        """Генерирует уникальный state для провайдера"""
        state = secrets.token_urlsafe(32)
        self._states[state] = {
            "provider": provider,
            "created_at": datetime.now(UTC),
            "used": False,
        }
        # logger.info("Generated state", extra={"provider": provider, "state": state})
        return state

    def validate_state(self, state: str, provider: str) -> bool:
        """Проверяет валидность state"""
        # logger.info("validate_state", extra={"state": state, "provider": provider})

        # Проверяем, что state не обрабатывается в данный момент
        if state in self._processing_states:
            logger.warning("State is already being processed", extra={"state": state})
            return False

        if state not in self._states:
            logger.warning("Invalid state", extra={"state": state})
            return False

        state_data = self._states[state]

        # Проверяем провайдера
        if state_data["provider"] != provider:
            logger.warning(
                "State provider mismatch",
                extra={
                    "expected_provider": state_data["provider"],
                    "got_provider": provider,
                },
            )
            return False

        # Проверяем время жизни (5 минут)
        if datetime.now(UTC) - state_data["created_at"] > timedelta(minutes=5):
            logger.warning("State expired", extra={"state": state})
            return False

        # Проверяем, что state еще не использовался
        if state_data["used"]:
            logger.warning("State already used", extra={"state": state})
            return False

        # Помечаем как обрабатываемый
        self._processing_states.add(state)

        # Помечаем как использованный
        # logger.info("mark as used", extra={"state_data": state_data})
        state_data["used"] = True

        # Удаляем из множества обрабатываемых
        self._processing_states.discard(state)

        return True

    def validate_state_or_raise(self, state: str, provider: str) -> None:
        """Валидирует state, выбрасывает HTTPException при ошибке."""
        if not self.validate_state(state, provider):
            logger.exception("Invalid state parameter", extra={"state": state}, exc_info=True)
            raise HTTPException(status_code=400, detail="Invalid state parameter")

    def cleanup_expired_states(self) -> None:
        """Очищает истекшие state"""
        now = datetime.now(UTC)
        expired_states = [
            state for state, data in self._states.items() if now - data["created_at"] > timedelta(minutes=10)
        ]
        for state in expired_states:
            del self._states[state]
            # Также очищаем из множества обрабатываемых
            self._processing_states.discard(state)
        # if expired_states:
        # logger.info(
        #     "Cleaned up expired states", extra={"count": len(expired_states)}
        # )


async def cleanup_oauth_data() -> None:
    """Периодическая очистка OAuth данных"""
    while True:
        try:
            # Очищаем истекшие state
            state_storage.cleanup_expired_states()
            # logger.debug("OAuth data cleanup completed")

        except Exception:
            logger.exception("Error during OAuth cleanup", exc_info=True)

        # Очищаем каждые 5 минут
        await asyncio.sleep(300)


def start_cleanup_task() -> None:
    """Запускает задачу очистки"""
    asyncio.create_task(cleanup_oauth_data())


# Глобальный экземпляр
state_storage = StateStorage()
