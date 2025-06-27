from fastapi import APIRouter

from backend.core.database import async_session_maker
from backend.dao.user import UserDAO
from backend.logger import get_logger
from backend.schemas.user import User as SchemaUser

router = APIRouter(prefix="/users", tags=["Users"])

logger = get_logger(__name__)


@router.get("/", response_model=list[SchemaUser])
async def get_users() -> list[SchemaUser]:
    async with async_session_maker() as session:
        users = await UserDAO.get_all(session)
        logger.info("users: %s", users)
        return users


@router.get("/{user_id}", response_model=SchemaUser | None)
async def get_user(user_id: int) -> SchemaUser | None:
    async with async_session_maker() as session:
        return await UserDAO.get_one_or_none(session, id=user_id)
