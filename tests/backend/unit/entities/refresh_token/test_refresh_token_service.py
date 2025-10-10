"""Unit тесты для refresh_token service."""

from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

import pytest

from backend.entities.assemblers.schemas import SRefreshToken
from backend.entities.refresh_token.dao import RefreshTokenDAO
from backend.entities.refresh_token.service import RefreshTokenService


class TestRefreshTokenService:
    """Тесты для RefreshTokenService."""

    @pytest.fixture
    def mock_refresh_token_dao(self):
        """Мок для RefreshTokenDAO."""
        return Mock(spec=RefreshTokenDAO)

    @pytest.fixture
    def mock_user_service(self):
        """Мок для UserService."""
        return Mock()

    @pytest.fixture
    def refresh_token_service(self, mock_refresh_token_dao, mock_user_service):
        """Создание RefreshTokenService с моком DAO."""
        return RefreshTokenService(mock_refresh_token_dao, mock_user_service)

    @pytest.fixture
    def sample_refresh_token(self):
        """Образец refresh token для тестов."""
        return SRefreshToken(
            id=1,
            user_id=1,
            token="refresh_token_123",
            expires_at=datetime.now(UTC) + timedelta(days=7),
            is_revoked=False,
            created_at=datetime.now(UTC),
        )

    @pytest.mark.asyncio
    async def test_create_refresh_token_success(
        self, refresh_token_service, mock_refresh_token_dao, sample_refresh_token
    ):
        """Тест успешного создания refresh token."""
        # Настройка мока
        mock_refresh_token_dao.create.return_value = sample_refresh_token

        # Вызов метода
        result = await refresh_token_service.create_refresh_token(1)

        # Проверки
        assert result == sample_refresh_token
        mock_refresh_token_dao.create_refresh_token.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_refresh_token_by_token_success(
        self, refresh_token_service, mock_refresh_token_dao, sample_refresh_token
    ):
        """Тест успешного получения refresh token по токену."""
        # Настройка мока
        mock_refresh_token_dao.get_by_token.return_value = sample_refresh_token

        # Вызов метода
        result = await refresh_token_service.get_refresh_token_by_token("refresh_token_123")

        # Проверки
        assert result == sample_refresh_token
        mock_refresh_token_dao.get_refresh_token_by_token.assert_called_once_with("refresh_token_123")

    @pytest.mark.asyncio
    async def test_get_refresh_token_by_token_not_found(self, refresh_token_service, mock_refresh_token_dao):
        """Тест получения несуществующего refresh token по токену."""
        # Настройка мока
        mock_refresh_token_dao.get_by_token.return_value = None

        # Вызов метода
        result = await refresh_token_service.get_refresh_token_by_token("nonexistent_token")

        # Проверки
        assert result is None
        mock_refresh_token_dao.get_refresh_token_by_token.assert_called_once_with("nonexistent_token")

    @pytest.mark.asyncio
    async def test_validate_refresh_token_valid(
        self, refresh_token_service, mock_refresh_token_dao, sample_refresh_token
    ):
        """Тест валидации валидного refresh token."""
        # Настройка мока
        mock_refresh_token_dao.get_by_token.return_value = sample_refresh_token

        # Вызов метода
        result = await refresh_token_service.validate_refresh_token("refresh_token_123")

        # Проверки
        assert result == sample_refresh_token
        mock_refresh_token_dao.get_refresh_token_by_token.assert_called_once_with("refresh_token_123")

    @pytest.mark.asyncio
    async def test_validate_refresh_token_not_found(self, refresh_token_service, mock_refresh_token_dao):
        """Тест валидации несуществующего refresh token."""
        # Настройка мока
        mock_refresh_token_dao.get_by_token.return_value = None

        # Вызов метода
        result = await refresh_token_service.validate_refresh_token("nonexistent_token")

        # Проверки
        assert result is None
        mock_refresh_token_dao.get_refresh_token_by_token.assert_called_once_with("nonexistent_token")

    @pytest.mark.asyncio
    async def test_validate_refresh_token_revoked(self, refresh_token_service, mock_refresh_token_dao):
        """Тест валидации отозванного refresh token."""
        # Настройка мока
        revoked_token = SRefreshToken(
            id=1,
            user_id=1,
            token="revoked_token",
            expires_at=datetime.now(UTC) + timedelta(days=7),
            is_revoked=True,
            created_at=datetime.now(UTC),
        )
        mock_refresh_token_dao.get_refresh_token_by_token.return_value = revoked_token

        # Вызов метода
        result = await refresh_token_service.validate_refresh_token("revoked_token")

        # Проверки
        assert result is None
        mock_refresh_token_dao.get_refresh_token_by_token.assert_called_once_with("revoked_token")

    @pytest.mark.asyncio
    async def test_validate_refresh_token_expired(self, refresh_token_service, mock_refresh_token_dao):
        """Тест валидации истекшего refresh token."""
        # Настройка мока
        expired_token = SRefreshToken(
            id=1,
            user_id=1,
            token="expired_token",
            expires_at=datetime.now(UTC) - timedelta(days=1),  # Истек вчера
            is_revoked=False,
            created_at=datetime.now(UTC) - timedelta(days=8),
        )
        mock_refresh_token_dao.get_refresh_token_by_token.return_value = expired_token

        # Вызов метода
        result = await refresh_token_service.validate_refresh_token("expired_token")

        # Проверки
        assert result is None
        mock_refresh_token_dao.get_refresh_token_by_token.assert_called_once_with("expired_token")

    @pytest.mark.asyncio
    async def test_revoke_refresh_token_success(self, refresh_token_service, mock_refresh_token_dao):
        """Тест успешного отзыва refresh token."""
        # Настройка мока
        mock_refresh_token_dao.revoke_refresh_token.return_value = True

        # Вызов метода
        result = await refresh_token_service.revoke_refresh_token("refresh_token_123")

        # Проверки
        assert result is True
        mock_refresh_token_dao.revoke_refresh_token.assert_called_once_with("refresh_token_123")

    @pytest.mark.asyncio
    async def test_revoke_refresh_token_not_found(self, refresh_token_service, mock_refresh_token_dao):
        """Тест отзыва несуществующего refresh token."""
        # Настройка мока
        mock_refresh_token_dao.revoke_refresh_token.return_value = False

        # Вызов метода
        result = await refresh_token_service.revoke_refresh_token("nonexistent_token")

        # Проверки
        assert result is False
        mock_refresh_token_dao.revoke_refresh_token.assert_called_once_with("nonexistent_token")

    @pytest.mark.asyncio
    async def test_delete_refresh_token_success(self, refresh_token_service, mock_refresh_token_dao):
        """Тест успешного удаления refresh token."""
        # Настройка мока
        mock_refresh_token_dao.delete_refresh_token.return_value = True

        # Вызов метода
        result = await refresh_token_service.delete_refresh_token(1)

        # Проверки
        assert result is True
        mock_refresh_token_dao.delete_refresh_token.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_delete_refresh_token_not_found(self, refresh_token_service, mock_refresh_token_dao):
        """Тест удаления несуществующего refresh token."""
        # Настройка мока
        mock_refresh_token_dao.delete_refresh_token.return_value = False

        # Вызов метода
        result = await refresh_token_service.delete_refresh_token(999)

        # Проверки
        assert result is False
        mock_refresh_token_dao.delete_refresh_token.assert_called_once_with(999)

    @pytest.mark.asyncio
    async def test_get_user_refresh_tokens_success(
        self, refresh_token_service, mock_refresh_token_dao, sample_refresh_token
    ):
        """Тест успешного получения refresh tokens пользователя."""
        # Настройка мока
        mock_refresh_token_dao.get_user_refresh_tokens.return_value = [sample_refresh_token]

        # Вызов метода
        result = await refresh_token_service.get_user_refresh_tokens(1)

        # Проверки
        assert len(result) == 1
        assert result[0] == sample_refresh_token
        mock_refresh_token_dao.get_user_refresh_tokens.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_user_refresh_tokens_empty(self, refresh_token_service, mock_refresh_token_dao):
        """Тест получения пустого списка refresh tokens пользователя."""
        # Настройка мока
        mock_refresh_token_dao.get_user_refresh_tokens.return_value = []

        # Вызов метода
        result = await refresh_token_service.get_user_refresh_tokens(1)

        # Проверки
        assert result == []
        mock_refresh_token_dao.get_user_refresh_tokens.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens_success(self, refresh_token_service, mock_refresh_token_dao):
        """Тест успешного отзыва всех refresh tokens пользователя."""
        # Настройка мока
        mock_refresh_token_dao.revoke_all_user_tokens.return_value = 3  # Отозвано 3 токена

        # Вызов метода
        result = await refresh_token_service.revoke_all_user_tokens(1)

        # Проверки
        assert result == 3
        mock_refresh_token_dao.revoke_all_user_tokens.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_cleanup_expired_tokens_success(self, refresh_token_service, mock_refresh_token_dao):
        """Тест успешной очистки истекших refresh tokens."""
        # Настройка мока
        mock_refresh_token_dao.cleanup_expired_tokens.return_value = 5  # Удалено 5 токенов

        # Вызов метода
        result = await refresh_token_service.cleanup_expired_tokens()

        # Проверки
        assert result == 5
        mock_refresh_token_dao.cleanup_expired_tokens.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_token_valid_true(self, refresh_token_service, mock_refresh_token_dao, sample_refresh_token):
        """Тест проверки валидности токена - валидный."""
        # Настройка мока
        mock_refresh_token_dao.get_by_token.return_value = sample_refresh_token

        # Вызов метода
        result = await refresh_token_service.is_token_valid("refresh_token_123")

        # Проверки
        assert result is True
        mock_refresh_token_dao.get_refresh_token_by_token.assert_called_once_with("refresh_token_123")

    @pytest.mark.asyncio
    async def test_is_token_valid_false(self, refresh_token_service, mock_refresh_token_dao):
        """Тест проверки валидности токена - невалидный."""
        # Настройка мока
        mock_refresh_token_dao.get_by_token.return_value = None

        # Вызов метода
        result = await refresh_token_service.is_token_valid("invalid_token")

        # Проверки
        assert result is False
        mock_refresh_token_dao.get_refresh_token_by_token.assert_called_once_with("invalid_token")
