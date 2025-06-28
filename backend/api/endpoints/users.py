from fastapi import APIRouter

from backend.dao.user import UserDAO
from backend.logger import get_logger
from backend.schemas.user import User

router = APIRouter(prefix="/users", tags=["Users"])

logger = get_logger(__name__)


@router.get("/", response_model=list[User])
async def get_users() -> list[User]:
    users = await UserDAO.get_all()
    logger.info("users: %s", users)
    return users


@router.get("/{user_id}", response_model=User | None)
async def get_user(user_id: int) -> User | None:
    return await UserDAO.get_one_or_none(id=user_id)
