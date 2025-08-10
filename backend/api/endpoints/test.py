from fastapi import APIRouter
from pydantic import EmailStr

from backend.celery_app.utils.email import send_welcome_email_task
from backend.logger import get_logger


logger = get_logger(__name__)

router = APIRouter(
    prefix="/test",
    tags=["Test"],
)


@router.post("/send_email")
async def send_email(email_to: EmailStr, username: str) -> dict[str, str]:
    logger.info("Sending email")

    await send_welcome_email_task(
        user_email=email_to,
        username=username
    )

    return {"message": "Email sent"}
