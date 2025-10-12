import asyncio
from typing import Any

from backend.celery_app.app import celery_app
from backend.celery_app.utils.email import (
    _send_email_async,
    create_welcome_message,
)
from backend.core.logger import get_logger

logger = get_logger(__name__)


@celery_app.task(bind=True, max_retries=3)
def send_welcome_email(self: Any, user_email: str, username: str) -> dict[str, Any]:
    """
    Отправка приветственного письма новому пользователю.

    Args:
        user_email: Email пользователя
        username: Имя пользователя

    Returns:
        dict: Результат отправки
    """
    logger.info("Now in send_welcome_email", extra={"file": __file__})
    try:
        logger.info("Отправка приветственного письма", extra={"user_email": user_email})

        # Создаем сообщение
        message = create_welcome_message(user_email, username)

        logger.info("before call async _send_email_async")
        # Отправляем письмо
        asyncio.run(_send_email_async(message))

        logger.info("Приветственное письмо успешно отправлено", extra={"user_email": user_email})
        return {"status": "success", "email": user_email}

    except Exception as exc:
        logger.exception("Ошибка отправки письма", extra={"user_email": user_email}, exc_info=True)

        return {"status": "error", "email": user_email, "error": str(exc)}


async def send_welcome_email_task(user_email: str, username: str) -> None:
    """
    Отправляет приветственное письмо новому пользователю.

    Args:
        user_email: Email пользователя
        username: Имя пользователя
    """
    logger.info("Sending welcome email", extra={"user_email": user_email})
    try:
        # Запускаем задачу отправки письма
        send_welcome_email.delay(user_email, username)
        logger.info("Welcome email task queued for user", extra={"user_email": user_email})
    except Exception:
        # Не прерываем основной процесс, если не удалось отправить письмо
        logger.exception("Failed to queue welcome email task", exc_info=True)
