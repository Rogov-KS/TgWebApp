import asyncio

from fastapi import APIRouter
from fastapi_cache.decorator import cache
from fastapi_versioning import version
from pydantic import EmailStr

from backend.celery_app.tasks.email import send_welcome_email_task
from backend.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/test",
    tags=["Test"],
)


@router.post("/send_email")
@version(1)
async def send_email(email_to: EmailStr, username: str) -> dict[str, str]:
    """Отправка email"""
    logger.info("Sending email", extra={"email_to": email_to, "username": username})

    await send_welcome_email_task(user_email=email_to, username=username)

    return {"message": "Email sent"}


@router.get("/test_cache")
@version(1)
@cache(expire=30)
async def get_cache():
    """Тест кэша c"""
    logger.info("Start test cache")
    await asyncio.sleep(3)
    logger.info("End test cache")
    return {"hello": "world"}


@router.get("/sentry-debug")
@version(1)
async def trigger_error() -> None:
    """Тест Sentry"""
    1 / 0


@router.get("/versioning-test")
@version(1)
async def hello_version(name: str) -> dict[str, str]:
    """Тест Versioning"""
    return {"message": f"Hello {name}"}


@router.get("/versioning-test")
@version(2)
async def hello_version_v2(name: str) -> dict[str, str]:
    """Тест Versioning"""
    return {"message": f"Hello {name * 2}"}

@router.get("/ping")
@version(1)
async def ping() -> str:
    """Тестовый эндпоинт."""
    return "pong"
