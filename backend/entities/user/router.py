from fastapi import APIRouter
from fastapi_versioning import version

from backend.entities.user.schemas import User
from backend.entities.user.service import UserServiceDep

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[User])
@version(1)
async def get_users(user_service: UserServiceDep) -> list[User]:
    """Получить всех пользователей."""
    return await user_service.get_all_users()


@router.get("/{user_id}", response_model=User | None)
@version(1)
async def get_user(user_id: int, user_service: UserServiceDep) -> User | None:
    """Получить пользователя по ID."""
    return await user_service.get_user_by_id(user_id)
