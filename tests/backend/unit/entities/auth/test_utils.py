"""Unit тесты для auth utils."""

from backend.entities.auth.utils import (
    create_access_token,
    get_password_hash,
    is_valid_email,
    verify_password,
)


class TestPasswordUtils:
    """Тесты для работы с паролями."""

    def test_get_password_hash(self):
        """Тест хеширования пароля."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        # Проверяем что хеш не равен исходному паролю
        assert hashed != password
        # Проверяем что хеш не пустой
        assert len(hashed) > 0
        # Проверяем что хеш начинается с правильным префиксом bcrypt
        assert hashed.startswith("$2b$")

    def test_verify_password_correct(self):
        """Тест проверки правильного пароля."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Тест проверки неправильного пароля."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_none_hash(self):
        """Тест проверки пароля с None хешем."""
        password = "test_password_123"

        assert verify_password(password, None) is False

    def test_verify_password_empty_hash(self):
        """Тест проверки пароля с пустым хешем."""
        password = "test_password_123"

        assert verify_password(password, "") is False


class TestEmailUtils:
    """Тесты для работы с email."""

    def test_is_valid_email_valid_cases(self):
        """Тест валидных email адресов."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@test.com",
            "a@b.co",
        ]

        for email in valid_emails:
            assert is_valid_email(email) is True, f"Email {email} должен быть валидным"

    def test_is_valid_email_invalid_cases(self):
        """Тест невалидных email адресов."""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            "user..name@example.com",
            "",
            "user@domain",
            "user name@example.com",
        ]

        for email in invalid_emails:
            assert is_valid_email(email) is False, f"Email {email} должен быть невалидным"


class TestTokenUtils:
    """Тесты для работы с токенами."""

    def test_create_access_token(self):
        """Тест создания access token."""
        user_id = 123
        token = create_access_token(user_id)

        # Проверяем что токен не пустой
        assert len(token) > 0
        # Проверяем что токен содержит точки (JWT формат)
        assert token.count(".") == 2

    def test_create_access_token_different_users(self):
        """Тест создания токенов для разных пользователей."""
        user_id_1 = 123
        user_id_2 = 456

        token_1 = create_access_token(user_id_1)
        token_2 = create_access_token(user_id_2)

        # Токены должны быть разными для разных пользователей
        assert token_1 != token_2

    def test_create_access_token_same_user(self):
        """Тест создания токенов для одного пользователя."""
        user_id = 123

        token_1 = create_access_token(user_id)
        token_2 = create_access_token(user_id)

        # Токены могут быть разными из-за времени создания
        # Но оба должны быть валидными
        assert len(token_1) > 0
        assert len(token_2) > 0
