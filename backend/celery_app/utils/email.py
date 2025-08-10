from backend.celery_app.tasks.email import send_welcome_email
from backend.logger import get_logger

logger = get_logger(__name__)


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


async def send_password_reset_email_task(
    user_email: str, username: str, reset_token: str
) -> None:
    """
    Отправляет письмо для сброса пароля.

    Args:
        user_email: Email пользователя
        username: Имя пользователя
        reset_token: Токен для сброса пароля
    """
    try:
        # TODO: Реализовать задачу отправки письма для сброса пароля
        logger.info(
            "Password reset email task queued for user: %s",
            user_email
        )
    except Exception as e:
        logger.error("Failed to queue password reset email task: %s", e)


async def send_notification_email_task(
    user_email: str, subject: str, message: str
) -> None:
    """
    Отправляет уведомительное письмо пользователю.

    Args:
        user_email: Email пользователя
        subject: Тема письма
        message: Текст письма
    """
    try:
        # TODO: Реализовать задачу отправки уведомительных писем
        logger.info(
            "Notification email task queued for user: %s",
            user_email
        )
    except Exception as e:
        logger.error("Failed to queue notification email task: %s", e)
