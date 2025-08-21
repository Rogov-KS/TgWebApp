"""
Фикстуры для пользователей в тестах
"""
import pytest
import pytest_asyncio
from backend.entities.user.dao import UserDAO


@pytest.fixture
def user_data():
    """Тестовые данные пользователя."""
    return {
        "id": 1,
        "username": "test_user",
        "email": "test@example.com",
        "is_active": True,
        "is_admin": False,
    }


@pytest.fixture
def multiple_users_data():
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
async def test_user(test_db_session, user_data):
    """Создает тестового пользователя в БД."""

    dao = UserDAO(test_db_session)
    user = await dao.create(**user_data)
    return user


@pytest_asyncio.fixture
async def test_users(test_db_session, multiple_users_data):
    """Создает несколько тестовых пользователей в БД."""

    dao = UserDAO(test_db_session)
    users = []
    for user_data in multiple_users_data:
        user = await dao.create(**user_data)
        users.append(user)
    return users
