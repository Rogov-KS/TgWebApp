import asyncio
from typing import Any

from aiosmtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
import os

from backend.celery_app.app import celery_app
from backend.core.config import settings
from backend.logger import get_logger

logger = get_logger(__name__)

# Настройка Jinja2 для шаблонов
template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
env = Environment(loader=FileSystemLoader(template_dir))


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
        message = MIMEMultipart("alternative")
        message["Subject"] = "Добро пожаловать в TgWebApp!"
        message["From"] = f"Creator <{settings.SMTP_USER}>"
        message["To"] = user_email

        # Загружаем шаблон
        template = env.get_template("welcome_email.html")
        html_content = template.render(
            username=username,
            app_name="TgWebApp",
        )

        # Создаем текстовую версию
        text_content = f"""
Добро пожаловать в TgWebApp, {username}!

Мы рады приветствовать вас в нашем приложении.

С уважением,
Команда TgWebApp
        """

        # Добавляем содержимое
        text_part = MIMEText(text_content, "plain", "utf-8")
        html_part = MIMEText(html_content, "html", "utf-8")

        message.attach(text_part)
        message.attach(html_part)

        logger.info("before call async _send_email_async")
        # Отправляем письмо
        asyncio.run(_send_email_async(message))

        logger.info(f"Приветственное письмо успешно отправлено на {user_email}")
        return {"status": "success", "email": user_email}

    except Exception as exc:
        logger.error(f"Ошибка отправки письма на {user_email}: {exc}")

        return {"status": "error", "email": user_email, "error": str(exc)}


async def _send_email_async(message: MIMEMultipart) -> None:
    """
    Асинхронная отправка email.

    Args:
        message: Email сообщение
    """
    logger.info("Now in _send_email_async from file: %s", __file__)
    if not all([
        settings.SMTP_USER,
        settings.SMTP_PASS
    ]):
        logger.warning("Email настройки не настроены, пропускаем отправку")
        return

    smtp = SMTP(
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        # username=settings.SMTP_USER,
        # password=settings.SMTP_PASS,
        # use_tls=settings.SMTP_USE_TLS,
        # use_ssl=settings.SMTP_USE_SSL,
    )

    logger.info("before call smtp.connect")
    await smtp.connect()

    logger.info("before call smtp.login")
    if settings.SMTP_USER and settings.SMTP_PASS:
        await smtp.login(settings.SMTP_USER, settings.SMTP_PASS)

    logger.info("before call smtp.send_message")
    await smtp.send_message(message)

    logger.info("before call smtp.quit")
    await smtp.quit()
