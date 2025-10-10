"""Unit тесты для telegram utils."""

from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest

from backend.entities.telegram.schemas import TelegramInitData
from backend.entities.telegram.utils import (
    is_telegram_data_fresh,
    parse_telegram_init_data,
    validate_telegram_init_data,
)


class TestParseTelegramInitData:
    """Тесты для парсинга Telegram init data."""

    def test_parse_telegram_init_data_success(self):
        """Тест успешного парсинга init data."""
        init_data = (
            "user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22John%22%2C"
            "%22last_name%22%3A%22Doe%22%2C%22username%22%3A%22johndoe%22%2C"
            "%22language_code%22%3A%22en%22%7D&"
            "chat_instance=-1234567890123456789&"
            "chat_type=private&"
            "auth_date=1640995200&"
            "hash=test_hash_123"
        )

        result = parse_telegram_init_data(init_data)

        assert isinstance(result, TelegramInitData)
        assert result.user is not None
        assert result.user.id == 123456789
        assert result.user.first_name == "John"
        assert result.user.last_name == "Doe"
        assert result.user.username == "johndoe"
        assert result.user.language_code == "en"
        assert result.chat_instance == "-1234567890123456789"
        assert result.chat_type == "private"
        assert result.auth_date == 1640995200
        assert result.hash == "test_hash_123"

    def test_parse_telegram_init_data_without_user(self):
        """Тест парсинга init data без данных пользователя."""
        init_data = "chat_instance=-1234567890123456789&chat_type=private&auth_date=1640995200&hash=test_hash_123"

        result = parse_telegram_init_data(init_data)

        assert isinstance(result, TelegramInitData)
        assert result.user is None
        assert result.chat_instance == "-1234567890123456789"
        assert result.chat_type == "private"
        assert result.auth_date == 1640995200
        assert result.hash == "test_hash_123"

    def test_parse_telegram_init_data_invalid_json(self):
        """Тест парсинга init data с невалидным JSON."""
        init_data = "user=invalid_json&auth_date=1640995200&hash=test_hash_123"

        with pytest.raises(ValueError, match="Невалидные данные Telegram"):
            parse_telegram_init_data(init_data)

    def test_parse_telegram_init_data_missing_required_fields(self):
        """Тест парсинга init data с отсутствующими обязательными полями."""
        init_data = "user=%7B%7D"  # Только user без auth_date и hash

        with pytest.raises(ValueError, match="Невалидные данные Telegram"):
            parse_telegram_init_data(init_data)

    def test_parse_telegram_init_data_invalid_auth_date(self):
        """Тест парсинга init data с невалидным auth_date."""
        init_data = "user=%7B%22id%22%3A123456789%7D&auth_date=invalid_timestamp&hash=test_hash_123"

        with pytest.raises(ValueError, match="Невалидные данные Telegram"):
            parse_telegram_init_data(init_data)


class TestValidateTelegramInitData:
    """Тесты для валидации Telegram init data."""

    @patch("backend.entities.telegram.utils.settings")
    def test_validate_telegram_init_data_success(self, mock_settings):
        """Тест успешной валидации init data."""
        mock_settings.TG_BOT_TOKEN = "test_bot_token"

        # Создаем валидные данные
        init_data = "user=%7B%22id%22%3A123456789%7D&auth_date=1640995200&hash=test_hash_123"

        # Мокаем hmac.compare_digest для возврата True
        with patch("backend.entities.telegram.utils.hmac.compare_digest", return_value=True):
            result = validate_telegram_init_data(init_data)
            assert result is True

    @patch("backend.entities.telegram.utils.settings")
    def test_validate_telegram_init_data_invalid_hash(self, mock_settings):
        """Тест валидации init data с невалидным hash."""
        mock_settings.TG_BOT_TOKEN = "test_bot_token"

        init_data = "user=%7B%22id%22%3A123456789%7D&auth_date=1640995200&hash=invalid_hash"

        # Мокаем hmac.compare_digest для возврата False
        with patch("backend.entities.telegram.utils.hmac.compare_digest", return_value=False):
            result = validate_telegram_init_data(init_data)
            assert result is False

    def test_validate_telegram_init_data_missing_hash(self):
        """Тест валидации init data без hash."""
        init_data = "user=%7B%22id%22%3A123456789%7D&auth_date=1640995200"

        result = validate_telegram_init_data(init_data)
        assert result is False

    def test_validate_telegram_init_data_empty_string(self):
        """Тест валидации пустой строки."""
        result = validate_telegram_init_data("")
        assert result is False


class TestIsTelegramDataFresh:
    """Тесты для проверки свежести данных Telegram."""

    def test_is_telegram_data_fresh_recent(self):
        """Тест проверки свежих данных (менее 24 часов)."""
        # Текущее время минус 1 час
        recent_timestamp = int((datetime.now(UTC) - timedelta(hours=1)).timestamp())

        result = is_telegram_data_fresh(recent_timestamp)
        assert result is True

    def test_is_telegram_data_fresh_old(self):
        """Тест проверки устаревших данных (более 24 часов)."""
        # Текущее время минус 25 часов
        old_timestamp = int((datetime.now(UTC) - timedelta(hours=25)).timestamp())

        result = is_telegram_data_fresh(old_timestamp)
        assert result is False

    def test_is_telegram_data_fresh_exactly_24_hours(self):
        """Тест проверки данных ровно 24 часа назад."""
        # Текущее время минус ровно 24 часа
        exactly_24h_timestamp = int((datetime.now(UTC) - timedelta(hours=24)).timestamp())

        result = is_telegram_data_fresh(exactly_24h_timestamp)
        # Данные ровно 24 часа назад должны считаться устаревшими
        assert result is False

    def test_is_telegram_data_fresh_future(self):
        """Тест проверки данных из будущего."""
        # Время в будущем
        future_timestamp = int((datetime.now(UTC) + timedelta(hours=1)).timestamp())

        result = is_telegram_data_fresh(future_timestamp)
        # Данные из будущего должны считаться валидными (возможно, разница в часовых поясах)
        assert result is True

    def test_is_telegram_data_fresh_zero_timestamp(self):
        """Тест проверки нулевого timestamp."""
        result = is_telegram_data_fresh(0)
        assert result is False

    def test_is_telegram_data_fresh_negative_timestamp(self):
        """Тест проверки отрицательного timestamp."""
        result = is_telegram_data_fresh(-1)
        assert result is False
