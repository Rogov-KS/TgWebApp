from fastapi import APIRouter
from sqlalchemy import select

from backend.core.database import async_session_maker
from backend.logger import get_logger
from backend.models.user import User as DBUser
from backend.schemas.user import User as SchemaUser

router = APIRouter(prefix="/users", tags=["Users"])

logger = get_logger(__name__)


@router.get("/", response_model=list[SchemaUser])
async def get_users() -> list[SchemaUser]:
    async with async_session_maker() as session:
        query = select(DBUser)
        result = await session.execute(query)
        users = result.scalars().all()
        logger.info("users: %s", users)
        return [SchemaUser.model_validate(user) for user in users]
