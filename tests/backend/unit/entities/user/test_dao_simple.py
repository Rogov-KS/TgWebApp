"""Упрощенные unit тесты для user DAO."""

from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.entities.user.dao import UserDAO
from backend.entities.user.models import UserDB


class TestUserDAO:
    """Тесты для UserDAO."""

    @pytest.fixture
    def mock_db_session(self):
        """Мок для AsyncSession."""
        return Mock(spec=AsyncSession)

    @pytest.fixture
    def user_dao(self, mock_db_session):
        """Создание UserDAO с моком сессии."""
        return UserDAO(mock_db_session)

    @pytest.fixture
    def sample_user_model(self):
        """Образец модели UserDB для тестов."""
        user = Mock(spec=UserDB)
        user.id = 1
        user.username = "testuser"
        user.email = "test@example.com"
        user.telegram_id = None
        user.hashed_password = "$2b$12$test_hash"
        user.is_active = True
        user.is_admin = False
        return user

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_dao, mock_db_session, sample_user_model):
        """Тест успешного создания пользователя."""
        # Настройка мока
        mock_db_session.execute = AsyncMock()
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_user_model
        mock_db_session.execute.return_value = mock_result
        mock_db_session.commit = AsyncMock()

        # Данные для создания
        user_data = {"username": "testuser", "email": "test@example.com", "hashed_password": "$2b$12$test_hash"}

        # Вызов метода
        result = await user_dao.create(**user_data)

        # Проверки
        assert result == sample_user_model
        mock_db_session.execute.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_one_or_none_success(self, user_dao, mock_db_session, sample_user_model):
        """Тест успешного получения пользователя по фильтру."""
        # Настройка мока
        mock_db_session.execute = AsyncMock()
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_user_model
        mock_db_session.execute.return_value = mock_result

        # Вызов метода
        result = await user_dao.get_one_or_none(id=1)

        # Проверки
        assert result == sample_user_model
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_one_or_none_not_found(self, user_dao, mock_db_session):
        """Тест получения несуществующего пользователя."""
        # Настройка мока
        mock_db_session.execute = AsyncMock()
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        # Вызов метода
        result = await user_dao.get_one_or_none(id=999)

        # Проверки
        assert result is None
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_users_success(self, user_dao, mock_db_session, sample_user_model):
        """Тест успешного получения всех пользователей."""
        # Настройка мока
        mock_db_session.execute = AsyncMock()
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_user_model]
        mock_db_session.execute.return_value = mock_result

        # Вызов метода
        result = await user_dao.get_all()

        # Проверки
        assert result == [sample_user_model]
        mock_db_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_success(self, user_dao, mock_db_session, sample_user_model):
        """Тест успешного обновления пользователя."""
        # Настройка мока
        mock_db_session.execute = AsyncMock()
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_user_model
        mock_db_session.execute.return_value = mock_result
        mock_db_session.commit = AsyncMock()

        # Данные для обновления
        filters = {"id": 1}
        update_data = {"username": "newusername", "email": "new@example.com"}

        # Вызов метода
        result = await user_dao.update(filters, update_data)

        # Проверки
        assert result == sample_user_model
        mock_db_session.execute.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_success(self, user_dao, mock_db_session):
        """Тест успешного удаления пользователя."""
        # Настройка мока
        mock_db_session.execute = AsyncMock()
        mock_result = Mock()
        mock_result.rowcount = 1
        mock_db_session.execute.return_value = mock_result
        mock_db_session.commit = AsyncMock()

        # Вызов метода
        result = await user_dao.delete(id=1)

        # Проверки
        assert result is True
        mock_db_session.execute.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, user_dao, mock_db_session):
        """Тест удаления несуществующего пользователя."""
        # Настройка мока
        mock_db_session.execute = AsyncMock()
        mock_result = Mock()
        mock_result.rowcount = 0
        mock_db_session.execute.return_value = mock_result
        mock_db_session.commit = AsyncMock()

        # Вызов метода
        result = await user_dao.delete(id=999)

        # Проверки
        assert result is False
        mock_db_session.execute.assert_called_once()
        mock_db_session.commit.assert_called_once()
