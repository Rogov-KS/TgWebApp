from fastapi import APIRouter

from backend.core.database import async_session_maker
from backend.dao.user import UserDAO
from backend.logger import get_logger
from backend.schemas.user import User as SchemaUser

router = APIRouter(prefix="/users", tags=["Users"])

logger = get_logger(__name__)
user_dao = UserDAO()


@router.get("/", response_model=list[SchemaUser])
async def get_users() -> list[SchemaUser]:
    async with async_session_maker() as session:
        users = await user_dao.get_all(session)
        logger.info("users: %s", users)
        return [SchemaUser.model_validate(user) for user in users]
