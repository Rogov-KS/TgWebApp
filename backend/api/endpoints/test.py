from fastapi import APIRouter
from pydantic import EmailStr
from fastapi_cache.decorator import cache
import asyncio

from backend.celery_app.tasks.email import send_welcome_email_task
from backend.core.logger import get_logger


logger = get_logger(__name__)

router = APIRouter(
    prefix="/test",
    tags=["Test"],
)


@router.post("/send_email")
async def send_email(email_to: EmailStr, username: str) -> dict[str, str]:
    """Отправка email"""
    logger.info("Sending email", extra={"email_to": email_to, "username": username})

    await send_welcome_email_task(
        user_email=email_to,
        username=username
    )

    return {"message": "Email sent"}


@router.get("/test_cache")
@cache(expire=30)
async def get_cache():
    """Тест кэша c"""
    logger.info("Start test cache")
    await asyncio.sleep(3)
    logger.info("End test cache")
    return dict(hello="world")


@router.get("/sentry-debug")
async def trigger_error() -> None:
    """Тест Sentry"""
    division_by_zero = 1 / 0