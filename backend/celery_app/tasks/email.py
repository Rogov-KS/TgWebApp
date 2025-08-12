import asyncio
from typing import Any

from backend.celery_app.app import celery_app
from backend.core.logger import get_logger
from backend.celery_app.utils.email import (
    create_welcome_message,
    _send_email_async,
)


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
    logger.info("Now in send_welcome_email from file: %s", __file__)
    try:
        logger.info(f"Отправка приветственного письма на {user_email}")

        # Создаем сообщение
        message = create_welcome_message(user_email, username)

        logger.info("before call async _send_email_async")
        # Отправляем письмо
        asyncio.run(_send_email_async(message))

        logger.info(f"Приветственное письмо успешно отправлено на {user_email}")
        return {"status": "success", "email": user_email}

    except Exception as exc:
        logger.error(f"Ошибка отправки письма на {user_email}: {exc}")

        return {"status": "error", "email": user_email, "error": str(exc)}


async def send_welcome_email_task(user_email: str, username: str) -> None:
    """
    Отправляет приветственное письмо новому пользователю.

    Args:
        user_email: Email пользователя
        username: Имя пользователя
    """
    logger.info("Sending welcome email to %s", user_email)
    try:
        # Запускаем задачу отправки письма
        send_welcome_email.delay(user_email, username)
        # send_welcome_email.delay(
        #     user_email=user_email,
        #     username=username
        # )
        logger.info(
            "Welcome email task queued for user: %s",
            user_email
        )
    except Exception as e:
        logger.error("Failed to queue welcome email task: %s", e)
        # Не прерываем основной процесс, если не удалось отправить письмо
