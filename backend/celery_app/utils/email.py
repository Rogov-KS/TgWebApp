from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

from aiosmtplib import SMTP
from jinja2 import Environment, FileSystemLoader

from backend.core.config import settings
from backend.core.logger import get_logger

logger = get_logger(__name__)

template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
template_env = Environment(loader=FileSystemLoader(template_dir))


def create_welcome_message(user_email: str, username: str) -> MIMEMultipart:
    """
    Создает приветственное email сообщение.

    Args:
        user_email: Email пользователя
        username: Имя пользователя

    Returns:
        MIMEMultipart: Готовое email сообщение
    """
    # Создаем сообщение
    message = MIMEMultipart("alternative")
    message["Subject"] = "Добро пожаловать в TgWebApp!"
    message["From"] = f"Creator <{settings.SMTP_USER}>"
    message["To"] = user_email

    # Загружаем шаблоны
    html_template = template_env.get_template("welcome_email/welcome_email.html")
    text_template = template_env.get_template("welcome_email/welcome_email.txt")

    # Рендерим шаблоны
    template_vars = {
        "username": username,
        "app_name": "TgWebApp",
    }
    html_content = html_template.render(**template_vars)
    text_content = text_template.render(**template_vars)

    # Добавляем содержимое
    text_part = MIMEText(text_content, "plain", "utf-8")
    html_part = MIMEText(html_content, "html", "utf-8")

    message.attach(text_part)
    message.attach(html_part)

    return message


async def _send_email_async(message: MIMEMultipart) -> None:
    """
    Асинхронная отправка email.

    Args:
        message: Email сообщение
    """
    logger.info("Now in _send_email_async", extra={"file": __file__})
    if not all([settings.SMTP_USER, settings.SMTP_PASS]):
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
