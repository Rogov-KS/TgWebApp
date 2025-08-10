import secrets
from typing import Dict
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from backend.logger import get_logger

logger = get_logger(__name__)


class StateStorage:
    """Хранилище для OAuth state параметров"""

    def __init__(self) -> None:
        self._states: Dict[str, Dict] = {}
        # Множество для отслеживания обрабатываемых states
        self._processing_states: set = set()

    def generate_state(self, provider: str) -> str:
        """Генерирует уникальный state для провайдера"""
        state = secrets.token_urlsafe(32)
        self._states[state] = {
            "provider": provider,
            "created_at": datetime.now(timezone.utc),
            "used": False
        }
        logger.info("Generated state for %s: %s", provider, state)
        return state

    def validate_state(self, state: str, provider: str) -> bool:
        """Проверяет валидность state"""
        logger.info("validate_state : %s \n %s \n\n", state, provider)

        # Проверяем, что state не обрабатывается в данный момент
        if state in self._processing_states:
            logger.warning("State is already being processed: %s", state)
            return False

        if state not in self._states:
            logger.warning("Invalid state: %s", state)
            return False

        state_data = self._states[state]

        # Проверяем провайдера
        if state_data["provider"] != provider:
            logger.warning(
                "State provider mismatch. Expected: %s, Got: %s",
                state_data["provider"], provider
            )
            return False

        # Проверяем время жизни (5 минут)
        if datetime.now(timezone.utc) - state_data["created_at"] > timedelta(minutes=5):
            logger.warning("State expired: %s", state)
            return False

        # Проверяем, что state еще не использовался
        if state_data["used"]:
            logger.warning("State already used: %s", state)
            return False

        # Помечаем как обрабатываемый
        self._processing_states.add(state)

        # Помечаем как использованный
        logger.info("mark as used : %s", state_data)
        state_data["used"] = True

        # Удаляем из множества обрабатываемых
        self._processing_states.discard(state)

        return True

    def validate_state_or_raise(self, state: str, provider: str) -> None:
        """Валидирует state, выбрасывает HTTPException при ошибке."""
        if not self.validate_state(state, provider):
            logger.error("Invalid state parameter: %s", state)
            raise HTTPException(
                status_code=400, detail="Invalid state parameter"
            )

    def cleanup_expired_states(self) -> None:
        """Очищает истекшие state"""
        now = datetime.now(timezone.utc)
        expired_states = [
            state for state, data in self._states.items()
            if now - data["created_at"] > timedelta(minutes=10)
        ]
        for state in expired_states:
            del self._states[state]
            # Также очищаем из множества обрабатываемых
            self._processing_states.discard(state)
        if expired_states:
            logger.info("Cleaned up %d expired states", len(expired_states))


# Глобальный экземпляр
state_storage = StateStorage()
