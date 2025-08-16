from fastapi import APIRouter
from fastapi_versioning import version

from backend.entities.user.dao import UserDAO
from backend.core.logger import get_logger
from backend.entities.user.schemas import User


router = APIRouter(prefix="/users", tags=["Users"])

logger = get_logger(__name__)


@router.get("/", response_model=list[User])
@version(1)
async def get_users() -> list[User]:
    users = await UserDAO.get_all()
    logger.info("Retrieved users", extra={"count": len(users)})
    return users


@router.get("/{user_id}", response_model=User | None)
@version(1)
async def get_user(user_id: int) -> User | None:
    return await UserDAO.get_one_or_none(id=user_id)
