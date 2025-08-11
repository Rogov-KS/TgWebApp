from fastapi import APIRouter
from pydantic import EmailStr
from fastapi_cache.decorator import cache
import asyncio

from backend.celery_app.tasks.email import send_welcome_email_task
from backend.logger import get_logger


logger = get_logger(__name__)

router = APIRouter(
    prefix="/test",
    tags=["Test"],
)


@router.post("/send_email")
async def send_email(email_to: EmailStr, username: str) -> dict[str, str]:
    """Отправка email"""
    logger.info("Sending email")

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
