"""Integration тесты для telegram endpoints."""

from unittest.mock import patch

from httpx import AsyncClient
import pytest


class TestTelegramEndpoints:
    """Тесты для telegram endpoints."""

    @pytest.fixture
    def valid_telegram_init_data(self):
        """Валидные init data для тестов."""
        return (
            "user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22John%22%2C"
            "%22last_name%22%3A%22Doe%22%2C%22username%22%3A%22johndoe%22%2C"
            "%22language_code%22%3A%22en%22%7D&"
            "auth_date=1640995200&"
            "hash=test_hash_123"
        )

    @pytest.fixture
    def invalid_telegram_init_data(self):
        """Невалидные init data для тестов."""
        return "user=%7B%22id%22%3A123456789%7D&auth_date=1640995200&hash=invalid_hash"

    @pytest.fixture
    def stale_telegram_init_data(self):
        """Устаревшие init data для тестов."""
        return (
            "user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22John%22%7D&"
            "auth_date=1609459200&"  # 1 января 2021 года (устаревшие данные)
            "hash=test_hash_123"
        )

    @pytest.mark.asyncio
    async def test_telegram_auth_success_new_user(self, test_client: AsyncClient, valid_telegram_init_data):
        """Тест успешной авторизации нового пользователя через Telegram."""
        with (
            patch("backend.entities.telegram.utils.validate_telegram_init_data", return_value=True),
            patch("backend.entities.telegram.utils.parse_telegram_init_data") as mock_parse,
            patch("backend.entities.telegram.utils.is_telegram_data_fresh", return_value=True),
        ):
            # Настраиваем возвращаемые данные парсинга
            mock_parse.return_value = Mock(
                user=Mock(id=123456789, first_name="John", last_name="Doe", username="johndoe", language_code="en"),
                auth_date=1640995200,
                hash="test_hash_123",
            )

            # Данные для авторизации
            auth_data = {"init_data": valid_telegram_init_data}

            response = await test_client.post("/api/v1/auth/telegram/", json=auth_data)

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data

            # Проверяем что cookies установлены
            assert "access_token" in response.cookies
            assert "refresh_token" in response.cookies

    @pytest.mark.asyncio
    async def test_telegram_auth_success_existing_user(self, test_client: AsyncClient, valid_telegram_init_data):
        """Тест успешной авторизации существующего пользователя через Telegram."""
        # Сначала создаем пользователя через обычную регистрацию
        user_data = {"username": "johndoe", "email": "john@example.com", "password": "password123"}
        await test_client.post("/api/v1/auth/register", json=user_data)

        with (
            patch("backend.entities.telegram.utils.validate_telegram_init_data", return_value=True),
            patch("backend.entities.telegram.utils.parse_telegram_init_data") as mock_parse,
            patch("backend.entities.telegram.utils.is_telegram_data_fresh", return_value=True),
        ):
            # Настраиваем возвращаемые данные парсинга
            mock_parse.return_value = Mock(
                user=Mock(id=123456789, first_name="John", last_name="Doe", username="johndoe", language_code="en"),
                auth_date=1640995200,
                hash="test_hash_123",
            )

            # Данные для авторизации
            auth_data = {"init_data": valid_telegram_init_data}

            response = await test_client.post("/api/v1/auth/telegram/", json=auth_data)

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_telegram_auth_invalid_hash(self, test_client: AsyncClient, invalid_telegram_init_data):
        """Тест авторизации с невалидным hash."""
        with patch("backend.entities.telegram.utils.validate_telegram_init_data", return_value=False):
            auth_data = {"init_data": invalid_telegram_init_data}

            response = await test_client.post("/api/v1/auth/telegram/", json=auth_data)

            assert response.status_code == 401
            data = response.json()
            assert "Невалидные данные Telegram" in data["detail"]

    @pytest.mark.asyncio
    async def test_telegram_auth_stale_data(self, test_client: AsyncClient, stale_telegram_init_data):
        """Тест авторизации с устаревшими данными."""
        with (
            patch("backend.entities.telegram.utils.validate_telegram_init_data", return_value=True),
            patch("backend.entities.telegram.utils.parse_telegram_init_data") as mock_parse,
            patch("backend.entities.telegram.utils.is_telegram_data_fresh", return_value=False),
        ):
            # Настраиваем возвращаемые данные парсинга
            mock_parse.return_value = Mock(user=Mock(id=123456789), auth_date=1609459200, hash="test_hash_123")

            auth_data = {"init_data": stale_telegram_init_data}

            response = await test_client.post("/api/v1/auth/telegram/", json=auth_data)

            assert response.status_code == 401
            data = response.json()
            assert "Данные авторизации устарели" in data["detail"]

    @pytest.mark.asyncio
    async def test_telegram_auth_no_user_data(self, test_client: AsyncClient):
        """Тест авторизации без данных пользователя."""
        init_data_without_user = "auth_date=1640995200&hash=test_hash_123"

        with (
            patch("backend.entities.telegram.utils.validate_telegram_init_data", return_value=True),
            patch("backend.entities.telegram.utils.parse_telegram_init_data") as mock_parse,
            patch("backend.entities.telegram.utils.is_telegram_data_fresh", return_value=True),
        ):
            # Настраиваем возвращаемые данные парсинга без пользователя
            mock_parse.return_value = Mock(user=None, auth_date=1640995200, hash="test_hash_123")

            auth_data = {"init_data": init_data_without_user}

            response = await test_client.post("/api/v1/auth/telegram/", json=auth_data)

            assert response.status_code == 401
            data = response.json()
            assert "Данные пользователя не найдены" in data["detail"]

    @pytest.mark.asyncio
    async def test_telegram_auth_missing_init_data(self, test_client: AsyncClient):
        """Тест авторизации без init_data."""
        auth_data = {}  # Отсутствует init_data

        response = await test_client.post("/api/v1/auth/telegram/", json=auth_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_telegram_auth_empty_init_data(self, test_client: AsyncClient):
        """Тест авторизации с пустым init_data."""
        auth_data = {"init_data": ""}

        response = await test_client.post("/api/v1/auth/telegram/", json=auth_data)

        assert response.status_code == 401
        data = response.json()
        assert "Невалидные данные Telegram" in data["detail"]

    @pytest.mark.asyncio
    async def test_telegram_auth_invalid_json_format(self, test_client: AsyncClient):
        """Тест авторизации с невалидным JSON в init_data."""
        invalid_json_init_data = "user=invalid_json&auth_date=1640995200&hash=test_hash_123"

        with patch("backend.entities.telegram.utils.validate_telegram_init_data", return_value=True):
            auth_data = {"init_data": invalid_json_init_data}

            response = await test_client.post("/api/v1/auth/telegram/", json=auth_data)

            assert response.status_code == 500  # Internal server error

    @pytest.mark.asyncio
    async def test_telegram_auth_creates_user_with_username(self, test_client: AsyncClient, valid_telegram_init_data):
        """Тест создания пользователя с username через Telegram."""
        with (
            patch("backend.entities.telegram.utils.validate_telegram_init_data", return_value=True),
            patch("backend.entities.telegram.utils.parse_telegram_init_data") as mock_parse,
            patch("backend.entities.telegram.utils.is_telegram_data_fresh", return_value=True),
        ):
            # Настраиваем возвращаемые данные парсинга с username
            mock_parse.return_value = Mock(
                user=Mock(id=123456789, first_name="John", last_name="Doe", username="johndoe", language_code="en"),
                auth_date=1640995200,
                hash="test_hash_123",
            )

            auth_data = {"init_data": valid_telegram_init_data}

            response = await test_client.post("/api/v1/auth/telegram/", json=auth_data)

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_telegram_auth_creates_user_without_username(self, test_client: AsyncClient):
        """Тест создания пользователя без username через Telegram."""
        init_data_without_username = (
            "user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22John%22%7D&auth_date=1640995200&hash=test_hash_123"
        )

        with (
            patch("backend.entities.telegram.utils.validate_telegram_init_data", return_value=True),
            patch("backend.entities.telegram.utils.parse_telegram_init_data") as mock_parse,
            patch("backend.entities.telegram.utils.is_telegram_data_fresh", return_value=True),
        ):
            # Настраиваем возвращаемые данные парсинга без username
            mock_parse.return_value = Mock(
                user=Mock(id=123456789, first_name="John", last_name=None, username=None, language_code="en"),
                auth_date=1640995200,
                hash="test_hash_123",
            )

            auth_data = {"init_data": init_data_without_username}

            response = await test_client.post("/api/v1/auth/telegram/", json=auth_data)

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
