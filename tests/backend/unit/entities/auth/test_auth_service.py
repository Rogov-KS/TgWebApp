"""Unit тесты для auth service."""

from unittest.mock import Mock

from fastapi import HTTPException
import pytest

from backend.entities.assemblers.schemas import SUser, SUserAuth, SUserLogin
from backend.entities.auth.service import AuthService
from backend.entities.refresh_token.service import RefreshTokenService
from backend.entities.user.service import UserService


class TestAuthService:
    """Тесты для AuthService."""

    @pytest.fixture
    def mock_user_service(self):
        """Мок для UserService."""
        return Mock(spec=UserService)

    @pytest.fixture
    def mock_refresh_service(self):
        """Мок для RefreshTokenService."""
        return Mock(spec=RefreshTokenService)

    @pytest.fixture
    def auth_service(self, mock_user_service, mock_refresh_service):
        """Создание AuthService с моками."""
        return AuthService(mock_user_service, mock_refresh_service)

    @pytest.fixture
    def sample_user(self):
        """Образец пользователя для тестов."""
        from datetime import datetime

        return SUser(
            id=1,
            username="testuser",
            email="test@example.com",
            telegram_id=None,
            hashed_password="$2b$12$.w1mGxaCdXUHQVVTZQE.Let0SWK4ry5esbhijmDgKXoQss3WXZ4Ou",
            is_active=True,
            is_admin=False,
            created_at=datetime.now(),
        )

    @pytest.mark.asyncio
    async def test_authenticate_user_by_email_success(self, auth_service, mock_user_service, sample_user):
        """Тест успешной аутентификации по email."""
        # Настройка мока
        mock_user_service.get_user_by.return_value = sample_user

        # Вызов метода
        result = await auth_service.authenticate_user("test@example.com", "password123")

        # Проверки
        assert result is not None
        assert result.id == sample_user.id
        assert result.username == sample_user.username
        mock_user_service.get_user_by.assert_called_once_with(email="test@example.com")

    @pytest.mark.asyncio
    async def test_authenticate_user_by_username_success(self, auth_service, mock_user_service, sample_user):
        """Тест успешной аутентификации по username."""
        # Настройка мока
        mock_user_service.get_user_by.return_value = sample_user

        # Вызов метода
        result = await auth_service.authenticate_user("testuser", "password123")

        # Проверки
        assert result is not None
        assert result.id == sample_user.id
        mock_user_service.get_user_by.assert_called_once_with(username="testuser")

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, auth_service, mock_user_service, sample_user):
        """Тест аутентификации с неправильным паролем."""
        # Настройка мока
        mock_user_service.get_user_by.return_value = sample_user

        # Вызов метода с неправильным паролем
        result = await auth_service.authenticate_user("test@example.com", "wrong_password")

        # Проверки
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_user_not_found(self, auth_service, mock_user_service):
        """Тест аутентификации несуществующего пользователя."""
        # Настройка мока
        mock_user_service.get_user_by.return_value = None

        # Вызов метода
        result = await auth_service.authenticate_user("nonexistent@example.com", "password123")

        # Проверки
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_email_format(self, auth_service, mock_user_service):
        """Тест аутентификации с невалидным email."""
        # Настройка мока - не должен вызываться для невалидного email
        mock_user_service.get_user_by.return_value = None

        # Вызов метода с невалидным email
        result = await auth_service.authenticate_user("invalid-email", "password123")

        # Проверки
        assert result is None
        # Для невалидного email должен искаться по username
        mock_user_service.get_user_by.assert_called_once_with(username="invalid-email")

    @pytest.mark.asyncio
    async def test_authenticate_admin_user_success(self, auth_service, mock_user_service):
        """Тест успешной аутентификации админа."""
        from datetime import datetime

        admin_user = SUser(
            id=1,
            username="admin",
            email="admin@example.com",
            telegram_id=None,
            hashed_password="$2b$12$.w1mGxaCdXUHQVVTZQE.Let0SWK4ry5esbhijmDgKXoQss3WXZ4Ou",
            is_active=True,
            is_admin=True,
            created_at=datetime.now(),
        )

        # Настройка мока
        mock_user_service.get_user_by.return_value = admin_user

        # Вызов метода
        result = await auth_service.authenticate_admin_user("admin@example.com", "password123")

        # Проверки
        assert result is not None
        assert result.is_admin is True

    @pytest.mark.asyncio
    async def test_authenticate_admin_user_not_admin(self, auth_service, mock_user_service, sample_user):
        """Тест аутентификации обычного пользователя как админа."""
        # Настройка мока
        mock_user_service.get_user_by.return_value = sample_user

        # Вызов метода
        result = await auth_service.authenticate_admin_user("test@example.com", "password123")

        # Проверки
        assert result is None  # Обычный пользователь не может войти как админ

    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_service, mock_user_service, mock_refresh_service):
        """Тест успешной регистрации пользователя."""
        # Настройка мока
        from datetime import datetime

        new_user = SUser(
            id=1,
            username="newuser",
            email="new@example.com",
            telegram_id=None,
            hashed_password="$2b$12$.w1mGxaCdXUHQVVTZQE.Let0SWK4ry5esbhijmDgKXoQss3WXZ4Ou",
            is_active=True,
            is_admin=False,
            created_at=datetime.now(),
        )
        mock_user_service.get_user_by.return_value = None  # Пользователь не существует
        mock_user_service.create_user.return_value = new_user

        # Данные для регистрации
        user_data = SUserAuth(username="newuser", email="new@example.com", password="password123")

        # Вызов метода
        result = await auth_service.register_user(user_data)

        # Проверки
        assert result is not None
        assert result.username == "newuser"
        assert result.email == "new@example.com"
        mock_user_service.create_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_email_exists(self, auth_service, mock_user_service):
        """Тест регистрации с существующим email."""
        # Настройка мока для проверки существования пользователя
        from datetime import datetime

        existing_user = SUser(
            id=1,
            username="existing",
            email="existing@example.com",
            telegram_id=None,
            hashed_password="$2b$12$.w1mGxaCdXUHQVVTZQE.Let0SWK4ry5esbhijmDgKXoQss3WXZ4Ou",
            is_active=True,
            is_admin=False,
            created_at=datetime.now(),
        )
        mock_user_service.get_user_by.return_value = existing_user

        # Данные для регистрации
        user_data = SUserAuth(
            username="newuser",
            email="existing@example.com",  # Существующий email
            password="password123",
        )

        # Вызов метода должен вызвать исключение
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.register_user(user_data)

        # Проверки
        assert exc_info.value.status_code == 400
        assert "User already exists" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_login_user_success(self, auth_service, mock_user_service, mock_refresh_service):
        """Тест успешного входа пользователя."""
        # Настройка мока
        from datetime import datetime

        user = SUser(
            id=1,
            username="testuser",
            email="test@example.com",
            telegram_id=None,
            hashed_password="$2b$12$.w1mGxaCdXUHQVVTZQE.Let0SWK4ry5esbhijmDgKXoQss3WXZ4Ou",
            is_active=True,
            is_admin=False,
            created_at=datetime.now(),
        )
        mock_user_service.get_user_by.return_value = user
        mock_refresh_service.create_refresh_token.return_value = "refresh_token_123"

        # Данные для входа
        login_data = SUserLogin(username_or_email="test@example.com", password="password123")

        # Мок для Response
        mock_response = Mock()

        # Вызов метода
        result = await auth_service.login_user(login_data, mock_response)

        # Проверки
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["refresh_token"] == "refresh_token_123"
        mock_refresh_service.create_refresh_token.assert_called_once_with(user.id)

    @pytest.mark.asyncio
    async def test_login_user_invalid_credentials(self, auth_service, mock_user_service):
        """Тест входа с неверными данными."""
        # Настройка мока
        mock_user_service.get_user_by.return_value = None

        # Данные для входа
        login_data = SUserLogin(username_or_email="nonexistent@example.com", password="password123")

        # Мок для Response
        mock_response = Mock()

        # Вызов метода должен вызвать исключение
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.login_user(login_data, mock_response)

        # Проверки
        assert exc_info.value.status_code == 401
        assert "Invalid credentials" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_logout_user_success(self, auth_service, mock_refresh_service, sample_user):
        """Тест успешного выхода пользователя."""
        # Настройка мока
        mock_refresh_service.revoke_all_user_tokens.return_value = 1

        # Мок для Response
        mock_response = Mock()

        # Вызов метода
        result = await auth_service.logout_user(sample_user, mock_response)

        # Проверки
        assert result["message"] == "Successfully logged out"
        mock_refresh_service.revoke_all_user_tokens.assert_called_once_with(1)
