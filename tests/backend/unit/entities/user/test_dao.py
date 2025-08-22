"""
Unit тесты для UserDAO
"""
import pytest_asyncio
from backend.entities.user.dao import UserDAO


class TestUserDAO:
    """Тесты для UserDAO."""

    @pytest_asyncio.fixture
    async def dao(self, test_db_session):
        """Создает экземпляр UserDAO для тестов."""
        return UserDAO(test_db_session)

    class TestCreate:
        """Тесты для метода create."""

        async def test_create_user_success(self, test_db_session):
            """Тест успешного создания пользователя."""
            user_dao = UserDAO(test_db_session)
            user = await user_dao.create(
                username="John_4",
                is_admin=False,
                is_bot=False,
                is_active=True,
                max_score=10
            )
            assert user is not None

# Здесь будут тесты:
# - test_create_user
# - test_get_user_by_id
# - test_get_user_by_email
# - test_get_user_by_tg_id
# - test_update_user
# - test_delete_user
# - test_get_all_users
