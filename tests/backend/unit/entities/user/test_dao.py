"""
Unit тесты для UserDAO
"""
import pytest
import pytest_asyncio
from backend.entities.user.dao import UserDAO
from backend.entities.user.models import User


class TestUserDAO:
    """Тесты для UserDAO."""

    @pytest_asyncio.fixture
    async def dao(self, test_db_session):
        """Создает экземпляр UserDAO для тестов."""
        return UserDAO(test_db_session)

    class TestCreate:
        """Тесты для метода create."""

        async def test_create_user_success(self, dao, user_data):
            """Тест успешного создания пользователя."""
            user = await dao.create(**user_data)
            assert user is not None
            assert user.username == user_data["username"]

# Здесь будут тесты:
# - test_create_user
# - test_get_user_by_id
# - test_get_user_by_email
# - test_get_user_by_tg_id
# - test_update_user
# - test_delete_user
# - test_get_all_users
