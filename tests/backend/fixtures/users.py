"""
Фикстуры для пользователей в тестах
"""
import pytest
import pytest_asyncio
from backend.entities.user.dao import UserDAO
from backend.entities.user.models import UserDB
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def get_user_data() -> dict:
    """Тестовые данные пользователя."""
    return {
        "id": 1,
        "username": "test_user",
        "email": "test@example.com",
        "is_active": True,
        "is_admin": False,
    }


@pytest.fixture
def get_multiple_users_data() -> list[dict]:
    """Тестовые данные для нескольких пользователей."""
    return [
        {
            "id": 1,
            "username": "user1",
            "email": "user1@example.com",
            "is_active": True,
            "is_admin": False,
        },
        {
            "id": 2,
            "username": "user2",
            "email": "user2@example.com",
            "is_active": True,
            "is_admin": False,
        },
        {
            "id": 3,
            "username": "user3",
            "email": "user3@example.com",
            "is_active": True,
            "is_admin": False,
        },
    ]


@pytest_asyncio.fixture
async def insert_test_user(
    get_async_test_db_session: AsyncSession, get_user_data: dict
) -> UserDB:
    """Создает тестового пользователя в БД."""

    dao = UserDAO(get_async_test_db_session)
    user = await dao.create(**get_user_data)
    return user


@pytest_asyncio.fixture
async def insert_test_users(
    get_async_test_db_session: AsyncSession,
    get_multiple_users_data: list[dict],
) -> list[UserDB]:
    """Создает несколько тестовых пользователей в БД."""

    dao = UserDAO(get_async_test_db_session)
    users = []
    for user_data in get_multiple_users_data:
        user = await dao.create(**user_data)
        users.append(user)
    return users
