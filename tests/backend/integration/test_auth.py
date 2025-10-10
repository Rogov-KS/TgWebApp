"""Integration тесты для auth endpoints."""

from httpx import AsyncClient
import pytest


class TestAuthEndpoints:
    """Тесты для auth endpoints."""

    @pytest.mark.asyncio
    async def test_register_user_success(self, test_client: AsyncClient):
        """Тест успешной регистрации пользователя."""
        user_data = {"username": "testuser", "email": "test@example.com", "password": "password123"}

        response = await test_client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "id" in data
        assert data["is_active"] is True
        assert data["is_admin"] is False

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self, test_client: AsyncClient):
        """Тест регистрации с дублирующимся email."""
        # Сначала регистрируем пользователя
        user_data = {"username": "testuser1", "email": "test@example.com", "password": "password123"}
        await test_client.post("/api/v1/auth/register", json=user_data)

        # Пытаемся зарегистрировать другого пользователя с тем же email
        duplicate_user_data = {"username": "testuser2", "email": "test@example.com", "password": "password456"}

        response = await test_client.post("/api/v1/auth/register", json=duplicate_user_data)

        assert response.status_code == 400
        data = response.json()
        assert "уже существует" in data["detail"]

    @pytest.mark.asyncio
    async def test_register_user_invalid_email(self, test_client: AsyncClient):
        """Тест регистрации с невалидным email."""
        user_data = {"username": "testuser", "email": "invalid-email", "password": "password123"}

        response = await test_client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_user_weak_password(self, test_client: AsyncClient):
        """Тест регистрации со слабым паролем."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123",  # Слишком короткий пароль
        }

        response = await test_client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_user_success(self, test_client: AsyncClient):
        """Тест успешного входа пользователя."""
        # Сначала регистрируем пользователя
        user_data = {"username": "testuser", "email": "test@example.com", "password": "password123"}
        await test_client.post("/api/v1/auth/register", json=user_data)

        # Входим
        login_data = {"username_or_email": "test@example.com", "password": "password123"}

        response = await test_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

        # Проверяем что cookies установлены
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies

    @pytest.mark.asyncio
    async def test_login_user_by_username(self, test_client: AsyncClient):
        """Тест входа пользователя по username."""
        # Сначала регистрируем пользователя
        user_data = {"username": "testuser", "email": "test@example.com", "password": "password123"}
        await test_client.post("/api/v1/auth/register", json=user_data)

        # Входим по username
        login_data = {"username_or_email": "testuser", "password": "password123"}

        response = await test_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_login_user_wrong_password(self, test_client: AsyncClient):
        """Тест входа с неправильным паролем."""
        # Сначала регистрируем пользователя
        user_data = {"username": "testuser", "email": "test@example.com", "password": "password123"}
        await test_client.post("/api/v1/auth/register", json=user_data)

        # Пытаемся войти с неправильным паролем
        login_data = {"username_or_email": "test@example.com", "password": "wrongpassword"}

        response = await test_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "Неверные учетные данные" in data["detail"]

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, test_client: AsyncClient):
        """Тест входа несуществующего пользователя."""
        login_data = {"username_or_email": "nonexistent@example.com", "password": "password123"}

        response = await test_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 401
        data = response.json()
        assert "Неверные учетные данные" in data["detail"]

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, test_client: AsyncClient):
        """Тест успешного обновления токена."""
        # Сначала регистрируем и входим
        user_data = {"username": "testuser", "email": "test@example.com", "password": "password123"}
        await test_client.post("/api/v1/auth/register", json=user_data)

        login_data = {"username_or_email": "test@example.com", "password": "password123"}
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)

        # Получаем refresh token из cookies
        login_response.cookies.get("refresh_token")

        # Обновляем токен
        response = await test_client.post("/api/v1/auth/refresh")

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, test_client: AsyncClient):
        """Тест обновления токена с невалидным refresh token."""
        # Устанавливаем невалидный refresh token в cookies
        test_client.cookies.set("refresh_token", "invalid_token")

        response = await test_client.post("/api/v1/auth/refresh")

        assert response.status_code == 401
        data = response.json()
        assert "Невалидный refresh token" in data["detail"]

    @pytest.mark.asyncio
    async def test_logout_success(self, test_client: AsyncClient):
        """Тест успешного выхода."""
        # Сначала регистрируем и входим
        user_data = {"username": "testuser", "email": "test@example.com", "password": "password123"}
        await test_client.post("/api/v1/auth/register", json=user_data)

        login_data = {"username_or_email": "test@example.com", "password": "password123"}
        await test_client.post("/api/v1/auth/login", json=login_data)

        # Выходим
        response = await test_client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Выход выполнен успешно"

        # Проверяем что cookies очищены
        assert "access_token" not in response.cookies or response.cookies.get("access_token") == ""
        assert "refresh_token" not in response.cookies or response.cookies.get("refresh_token") == ""

    @pytest.mark.asyncio
    async def test_logout_without_auth(self, test_client: AsyncClient):
        """Тест выхода без авторизации."""
        response = await test_client.post("/api/v1/auth/logout")

        assert response.status_code == 401
        data = response.json()
        assert "Не авторизован" in data["detail"]

    @pytest.mark.asyncio
    async def test_register_user_missing_fields(self, test_client: AsyncClient):
        """Тест регистрации с отсутствующими полями."""
        user_data = {
            "username": "testuser"
            # Отсутствуют email и password
        }

        response = await test_client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_user_missing_fields(self, test_client: AsyncClient):
        """Тест входа с отсутствующими полями."""
        login_data = {
            "username_or_email": "test@example.com"
            # Отсутствует password
        }

        response = await test_client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == 422  # Validation error
