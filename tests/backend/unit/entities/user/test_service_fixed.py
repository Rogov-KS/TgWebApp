"""Unit тесты для user service."""

from unittest.mock import Mock

import pytest

from backend.entities.assemblers.schemas import SUser, SUserAuth, SUserAuthViaTelegram
from backend.entities.user.dao import UserDAO
from backend.entities.user.service import UserService


class TestUserService:
    """Тесты для UserService."""

    @pytest.fixture
    def mock_user_dao(self):
        """Мок для UserDAO."""
        return Mock(spec=UserDAO)

    @pytest.fixture
    def user_service(self, mock_user_dao):
        """Создание UserService с моком DAO."""
        return UserService(mock_user_dao)

    @pytest.fixture
    def sample_user(self):
        """Образец пользователя для тестов."""
        from datetime import datetime

        return SUser(
            id=1,
            username="testuser",
            email="test@example.com",
            telegram_id=None,
            hashed_password="$2b$12$test_hash",
            is_active=True,
            is_admin=False,
            created_at=datetime.now(),
        )

    @pytest.fixture
    def sample_telegram_user(self):
        """Образец пользователя Telegram для тестов."""
        from datetime import datetime

        return SUser(
            id=1,
            username="johndoe",
            email=None,
            telegram_id=123456789,
            hashed_password=None,
            is_active=True,
            is_admin=False,
            created_at=datetime.now(),
        )

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_service, mock_user_dao, sample_user):
        """Тест успешного создания пользователя."""
        # Настройка мока
        mock_user_dao.create.return_value = sample_user

        # Подготовка данных
        user_data = SUserAuth(username="testuser", email="test@example.com", password="password123")

        # Вызов метода
        result = await user_service.create_user(user_data)

        # Проверки
        assert result == sample_user
        mock_user_dao.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_telegram_user_success(self, user_service, mock_user_dao, sample_telegram_user):
        """Тест успешного создания пользователя через Telegram."""
        # Настройка мока
        mock_user_dao.create.return_value = sample_telegram_user

        # Подготовка данных
        user_data = SUserAuthViaTelegram(username="johndoe", telegram_id=123456789)

        # Вызов метода
        result = await user_service.create_telegram_user(user_data)

        # Проверки
        assert result == sample_telegram_user
        mock_user_dao.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, user_service, mock_user_dao, sample_user):
        """Тест успешного получения пользователя по ID."""
        # Настройка мока
        mock_user_dao.get_one_or_none.return_value = sample_user

        # Вызов метода
        result = await user_service.get_user_by_id(1)

        # Проверки
        assert result == sample_user
        mock_user_dao.get_one_or_none.assert_called_once_with(id=1)

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, user_service, mock_user_dao):
        """Тест получения несуществующего пользователя по ID."""
        # Настройка мока
        mock_user_dao.get_one_or_none.return_value = None

        # Вызов метода
        result = await user_service.get_user_by_id(999)

        # Проверки
        assert result is None
        mock_user_dao.get_one_or_none.assert_called_once_with(id=999)

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, user_service, mock_user_dao, sample_user):
        """Тест успешного получения пользователя по email."""
        # Настройка мока
        mock_user_dao.get_one_or_none.return_value = sample_user

        # Вызов метода
        result = await user_service.get_user_by(email="test@example.com")

        # Проверки
        assert result == sample_user
        mock_user_dao.get_one_or_none.assert_called_once_with(email="test@example.com")

    @pytest.mark.asyncio
    async def test_get_user_by_telegram_id_success(self, user_service, mock_user_dao, sample_telegram_user):
        """Тест успешного получения пользователя по telegram_id."""
        # Настройка мока
        mock_user_dao.get_one_or_none.return_value = sample_telegram_user

        # Вызов метода
        result = await user_service.get_user_by(telegram_id=123456789)

        # Проверки
        assert result == sample_telegram_user
        mock_user_dao.get_one_or_none.assert_called_once_with(telegram_id=123456789)

    @pytest.mark.asyncio
    async def test_get_user_by_username_success(self, user_service, mock_user_dao, sample_user):
        """Тест успешного получения пользователя по username."""
        # Настройка мока
        mock_user_dao.get_one_or_none.return_value = sample_user

        # Вызов метода
        result = await user_service.get_user_by(username="testuser")

        # Проверки
        assert result == sample_user
        mock_user_dao.get_one_or_none.assert_called_once_with(username="testuser")

    @pytest.mark.asyncio
    async def test_get_user_by_with_email(self, user_service, mock_user_dao, sample_user):
        """Тест получения пользователя с фильтром по email."""
        # Настройка мока
        mock_user_dao.get_one_or_none.return_value = sample_user

        # Вызов метода
        result = await user_service.get_user_by(email="test@example.com")

        # Проверки
        assert result == sample_user
        mock_user_dao.get_one_or_none.assert_called_once_with(email="test@example.com")

    @pytest.mark.asyncio
    async def test_get_user_by_with_username(self, user_service, mock_user_dao, sample_user):
        """Тест получения пользователя с фильтром по username."""
        # Настройка мока
        mock_user_dao.get_one_or_none.return_value = sample_user

        # Вызов метода
        result = await user_service.get_user_by(username="testuser")

        # Проверки
        assert result == sample_user
        mock_user_dao.get_one_or_none.assert_called_once_with(username="testuser")

    @pytest.mark.asyncio
    async def test_get_user_by_with_telegram_id(self, user_service, mock_user_dao, sample_telegram_user):
        """Тест получения пользователя с фильтром по telegram_id."""
        # Настройка мока
        mock_user_dao.get_one_or_none.return_value = sample_telegram_user

        # Вызов метода
        result = await user_service.get_user_by(telegram_id=123456789)

        # Проверки
        assert result == sample_telegram_user
        mock_user_dao.get_one_or_none.assert_called_once_with(telegram_id=123456789)

    @pytest.mark.asyncio
    async def test_get_user_by_multiple_filters(self, user_service, mock_user_dao, sample_user):
        """Тест получения пользователя с несколькими фильтрами."""
        # Настройка мока
        mock_user_dao.get_one_or_none.return_value = sample_user

        # Вызов метода
        result = await user_service.get_user_by(email="test@example.com", username="testuser")

        # Проверки
        assert result == sample_user
        mock_user_dao.get_one_or_none.assert_called_once_with(email="test@example.com", username="testuser")

    @pytest.mark.asyncio
    async def test_get_all_users_success(self, user_service, mock_user_dao, sample_user):
        """Тест успешного получения всех пользователей."""
        # Настройка мока
        mock_user_dao.get_all.return_value = [sample_user]

        # Вызов метода
        result = await user_service.get_all_users()

        # Проверки
        assert len(result) == 1
        assert result[0] == sample_user
        mock_user_dao.get_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_users_empty(self, user_service, mock_user_dao):
        """Тест получения пустого списка пользователей."""
        # Настройка мока
        mock_user_dao.get_all.return_value = []

        # Вызов метода
        result = await user_service.get_all_users()

        # Проверки
        assert result == []
        mock_user_dao.get_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_success(self, user_service, mock_user_dao, sample_user):
        """Тест успешного обновления пользователя."""
        # Подготовка данных
        updated_user = sample_user.model_copy()
        updated_user.username = "updated_user"

        # Настройка мока
        mock_user_dao.update.return_value = updated_user

        # Вызов метода
        result = await user_service.update_user(filter_by={"id": 1}, update_data={"username": "updated_user"})

        # Проверки
        assert result == updated_user
        mock_user_dao.update.assert_called_once_with(filter_by={"id": 1}, update_data={"username": "updated_user"})
