"""Unit тесты для telegram service."""

from unittest.mock import Mock, patch

from fastapi import HTTPException
import pytest

from backend.entities.assemblers.schemas import SUser, SUserAuthViaTelegram
from backend.entities.refresh_token.service import RefreshTokenService
from backend.entities.telegram.schemas import TelegramUserData
from backend.entities.telegram.service import TelegramAuthService
from backend.entities.user.service import UserService


class TestTelegramAuthService:
    """Тесты для TelegramAuthService."""

    @pytest.fixture
    def mock_user_service(self):
        """Мок для UserService."""
        return Mock(spec=UserService)

    @pytest.fixture
    def mock_refresh_service(self):
        """Мок для RefreshTokenService."""
        return Mock(spec=RefreshTokenService)

    @pytest.fixture
    def telegram_service(self, mock_user_service, mock_refresh_service):
        """Создание TelegramAuthService с моками."""
        return TelegramAuthService(mock_user_service, mock_refresh_service)

    @pytest.fixture
    def sample_telegram_user(self):
        """Образец пользователя Telegram для тестов."""
        return TelegramUserData(
            id=123456789,
            first_name="John",
            last_name="Doe",
            username="johndoe",
            language_code="en",
            is_premium=False,
            photo_url="https://example.com/photo.jpg",
        )

    @pytest.fixture
    def sample_user(self):
        """Образец пользователя для тестов."""
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

    @pytest.fixture
    def valid_init_data(self):
        """Валидные init data для тестов."""
        return (
            "user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22John%22%2C"
            "%22last_name%22%3A%22Doe%22%2C%22username%22%3A%22johndoe%22%2C"
            "%22language_code%22%3A%22en%22%7D&"
            "auth_date=1640995200&"
            "hash=test_hash_123"
        )

    @pytest.mark.asyncio
    async def test_authenticate_telegram_user_success_existing_user(
        self,
        telegram_service,
        mock_user_service,
        mock_refresh_service,
        sample_telegram_user,
        sample_user,
        valid_init_data,
    ):
        """Тест успешной аутентификации существующего пользователя."""
        # Настройка моков
        mock_user_service.get_user_by.return_value = sample_user
        mock_refresh_service.create_refresh_token.return_value = "refresh_token_123"

        # Мок для Response
        mock_response = Mock()

        # Мокаем валидацию и парсинг
        with (
            patch("backend.entities.telegram.utils.validate_telegram_init_data", return_value=True),
            patch("backend.entities.telegram.utils.parse_telegram_init_data") as mock_parse,
            patch("backend.entities.telegram.utils.is_telegram_data_fresh", return_value=True),
            patch("backend.entities.auth.utils.create_access_token", return_value="access_token_123"),
            patch("backend.entities.auth.utils.set_auth_cookies"),
        ):
            # Настраиваем возвращаемые данные парсинга
            mock_parse.return_value = Mock(user=sample_telegram_user, auth_date=1640995200, hash="test_hash_123")

            # Вызов метода
            result = await telegram_service.authenticate_telegram_user(valid_init_data, mock_response)

            # Проверки
            assert "access_token" in result
            assert "refresh_token" in result
            assert result["access_token"] == "access_token_123"
            assert result["refresh_token"] == "refresh_token_123"
            mock_user_service.get_user_by.assert_called_once_with(telegram_id=123456789)
            mock_refresh_service.create_refresh_token.assert_called_once_with(sample_user.id)

    @pytest.mark.asyncio
    async def test_authenticate_telegram_user_success_new_user(
        self,
        telegram_service,
        mock_user_service,
        mock_refresh_service,
        sample_telegram_user,
        sample_user,
        valid_init_data,
    ):
        """Тест успешной аутентификации нового пользователя."""
        # Настройка моков - пользователь не найден, создаем нового
        mock_user_service.get_user_by.return_value = None
        mock_user_service.create_user.return_value = sample_user
        mock_refresh_service.create_refresh_token.return_value = "refresh_token_123"

        # Мок для Response
        mock_response = Mock()

        # Мокаем валидацию и парсинг
        with (
            patch("backend.entities.telegram.utils.validate_telegram_init_data", return_value=True),
            patch("backend.entities.telegram.utils.parse_telegram_init_data") as mock_parse,
            patch("backend.entities.telegram.utils.is_telegram_data_fresh", return_value=True),
            patch("backend.entities.auth.utils.create_access_token", return_value="access_token_123"),
            patch("backend.entities.auth.utils.set_auth_cookies"),
        ):
            # Настраиваем возвращаемые данные парсинга
            mock_parse.return_value = Mock(user=sample_telegram_user, auth_date=1640995200, hash="test_hash_123")

            # Вызов метода
            result = await telegram_service.authenticate_telegram_user(valid_init_data, mock_response)

            # Проверки
            assert "access_token" in result
            assert "refresh_token" in result
            mock_user_service.get_user_by.assert_called_once_with(telegram_id=123456789)
            mock_user_service.create_user.assert_called_once()
            mock_refresh_service.create_refresh_token.assert_called_once_with(sample_user.id)

    @pytest.mark.asyncio
    async def test_authenticate_telegram_user_invalid_data(self, telegram_service, valid_init_data):
        """Тест аутентификации с невалидными данными."""
        # Мок для Response
        mock_response = Mock()

        # Мокаем валидацию для возврата False
        with patch("backend.entities.telegram.utils.validate_telegram_init_data", return_value=False):
            # Вызов метода должен вызвать исключение
            with pytest.raises(HTTPException) as exc_info:
                await telegram_service.authenticate_telegram_user(valid_init_data, mock_response)

            # Проверки
            assert exc_info.value.status_code == 401
            assert "Невалидные данные Telegram" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_authenticate_telegram_user_stale_data(self, telegram_service, valid_init_data):
        """Тест аутентификации с устаревшими данными."""
        # Мок для Response
        mock_response = Mock()

        # Мокаем валидацию и проверку свежести
        with (
            patch("backend.entities.telegram.utils.validate_telegram_init_data", return_value=True),
            patch("backend.entities.telegram.utils.parse_telegram_init_data") as mock_parse,
            patch("backend.entities.telegram.utils.is_telegram_data_fresh", return_value=False),
        ):
            # Настраиваем возвращаемые данные парсинга
            mock_parse.return_value = Mock(user=Mock(id=123456789), auth_date=1640995200, hash="test_hash_123")

            # Вызов метода должен вызвать исключение
            with pytest.raises(HTTPException) as exc_info:
                await telegram_service.authenticate_telegram_user(valid_init_data, mock_response)

            # Проверки
            assert exc_info.value.status_code == 401
            assert "Невалидные данные Telegram" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_authenticate_telegram_user_no_user_data(self, telegram_service, valid_init_data):
        """Тест аутентификации без данных пользователя."""
        # Мок для Response
        mock_response = Mock()

        # Мокаем валидацию и парсинг
        with (
            patch("backend.entities.telegram.utils.validate_telegram_init_data", return_value=True),
            patch("backend.entities.telegram.utils.parse_telegram_init_data") as mock_parse,
            patch("backend.entities.telegram.utils.is_telegram_data_fresh", return_value=True),
        ):
            # Настраиваем возвращаемые данные парсинга без пользователя
            mock_parse.return_value = Mock(user=None, auth_date=1640995200, hash="test_hash_123")

            # Вызов метода должен вызвать исключение
            with pytest.raises(HTTPException) as exc_info:
                await telegram_service.authenticate_telegram_user(valid_init_data, mock_response)

            # Проверки
            assert exc_info.value.status_code == 401
            assert "Невалидные данные Telegram" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_or_create_telegram_user_existing(
        self, telegram_service, mock_user_service, sample_telegram_user, sample_user
    ):
        """Тест получения существующего пользователя."""
        # Настройка мока
        mock_user_service.get_user_by.return_value = sample_user

        # Вызов метода
        result = await telegram_service._get_or_create_telegram_user(sample_telegram_user)

        # Проверки
        assert result == sample_user
        mock_user_service.get_user_by.assert_called_once_with(telegram_id=123456789)

    @pytest.mark.asyncio
    async def test_get_or_create_telegram_user_new(
        self, telegram_service, mock_user_service, sample_telegram_user, sample_user
    ):
        """Тест создания нового пользователя."""
        # Настройка мока
        mock_user_service.get_user_by.return_value = None
        mock_user_service.create_user.return_value = sample_user

        # Вызов метода
        result = await telegram_service._get_or_create_telegram_user(sample_telegram_user)

        # Проверки
        assert result == sample_user
        mock_user_service.get_user_by.assert_called_once_with(telegram_id=123456789)
        mock_user_service.create_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_telegram_user_success(
        self, telegram_service, mock_user_service, sample_telegram_user, sample_user
    ):
        """Тест создания пользователя из данных Telegram."""
        # Настройка мока
        mock_user_service.create_user.return_value = sample_user

        # Вызов метода
        result = await telegram_service._create_telegram_user(sample_telegram_user)

        # Проверки
        assert result == sample_user
        mock_user_service.create_user.assert_called_once()

        # Проверяем что переданы правильные данные
        call_args = mock_user_service.create_user.call_args[0][0]
        assert isinstance(call_args, SUserAuthViaTelegram)
        assert call_args.username == "johndoe"
        assert call_args.telegram_id == 123456789

    @pytest.mark.asyncio
    async def test_create_telegram_user_without_username(self, telegram_service, mock_user_service, sample_user):
        """Тест создания пользователя без username."""
        # Создаем пользователя без username
        telegram_user_no_username = TelegramUserData(
            id=123456789,
            first_name="John",
            last_name="Doe",
            username=None,
            language_code="en",
            is_premium=False,
            photo_url=None,
        )

        # Настройка мока
        mock_user_service.create_user.return_value = sample_user

        # Вызов метода
        result = await telegram_service._create_telegram_user(telegram_user_no_username)

        # Проверки
        assert result == sample_user
        mock_user_service.create_user.assert_called_once()

        # Проверяем что username сгенерирован
        call_args = mock_user_service.create_user.call_args[0][0]
        assert call_args.username == "tg_user_123456789"
