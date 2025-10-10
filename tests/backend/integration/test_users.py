"""Integration тесты для user endpoints."""

from httpx import AsyncClient
import pytest


class TestUserEndpoints:
    """Тесты для user endpoints."""

    @pytest.fixture
    async def authenticated_user(self, test_client: AsyncClient):
        """Создает авторизованного пользователя для тестов."""
        # Регистрируем пользователя
        user_data = {"username": "testuser", "email": "test@example.com", "password": "password123"}
        await test_client.post("/api/v1/auth/register", json=user_data)

        # Входим
        login_data = {"username_or_email": "test@example.com", "password": "password123"}
        response = await test_client.post("/api/v1/auth/login", json=login_data)

        # Возвращаем cookies для использования в других тестах
        return response.cookies

    @pytest.mark.asyncio
    async def test_get_users_success(self, test_client: AsyncClient, authenticated_user):
        """Тест успешного получения списка пользователей."""
        # Устанавливаем cookies авторизованного пользователя
        test_client.cookies.update(authenticated_user)

        response = await test_client.get("/api/v1/users/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Проверяем структуру пользователя
        user = data[0]
        assert "id" in user
        assert "username" in user
        assert "email" in user
        assert "is_active" in user
        assert "is_admin" in user

    @pytest.mark.asyncio
    async def test_get_users_without_auth(self, test_client: AsyncClient):
        """Тест получения списка пользователей без авторизации."""
        response = await test_client.get("/api/v1/users/")

        assert response.status_code == 401
        data = response.json()
        assert "Не авторизован" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, test_client: AsyncClient, authenticated_user):
        """Тест успешного получения пользователя по ID."""
        # Устанавливаем cookies авторизованного пользователя
        test_client.cookies.update(authenticated_user)

        response = await test_client.get("/api/v1/users/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "username" in data
        assert "email" in data

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, test_client: AsyncClient, authenticated_user):
        """Тест получения несуществующего пользователя по ID."""
        # Устанавливаем cookies авторизованного пользователя
        test_client.cookies.update(authenticated_user)

        response = await test_client.get("/api/v1/users/999")

        assert response.status_code == 404
        data = response.json()
        assert "Пользователь не найден" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_user_by_id_without_auth(self, test_client: AsyncClient):
        """Тест получения пользователя по ID без авторизации."""
        response = await test_client.get("/api/v1/users/1")

        assert response.status_code == 401
        data = response.json()
        assert "Не авторизован" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_user_me_success(self, test_client: AsyncClient, authenticated_user):
        """Тест успешного получения текущего пользователя."""
        # Устанавливаем cookies авторизованного пользователя
        test_client.cookies.update(authenticated_user)

        response = await test_client.get("/api/v1/users/me")

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["is_active"] is True
        assert data["is_admin"] is False

    @pytest.mark.asyncio
    async def test_get_user_me_without_auth(self, test_client: AsyncClient):
        """Тест получения текущего пользователя без авторизации."""
        response = await test_client.get("/api/v1/users/me")

        assert response.status_code == 401
        data = response.json()
        assert "Не авторизован" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_users_multiple_users(self, test_client: AsyncClient):
        """Тест получения списка нескольких пользователей."""
        # Создаем несколько пользователей
        users_data = [
            {"username": "user1", "email": "user1@example.com", "password": "password123"},
            {"username": "user2", "email": "user2@example.com", "password": "password123"},
        ]

        for user_data in users_data:
            await test_client.post("/api/v1/auth/register", json=user_data)

        # Входим как первый пользователь
        login_data = {"username_or_email": "user1@example.com", "password": "password123"}
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)

        # Получаем список пользователей
        response = await test_client.get("/api/v1/users/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

        # Проверяем что все пользователи в списке
        usernames = [user["username"] for user in data]
        assert "user1" in usernames
        assert "user2" in usernames

    @pytest.mark.asyncio
    async def test_get_user_invalid_id(self, test_client: AsyncClient, authenticated_user):
        """Тест получения пользователя с невалидным ID."""
        # Устанавливаем cookies авторизованного пользователя
        test_client.cookies.update(authenticated_user)

        response = await test_client.get("/api/v1/users/invalid_id")

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_user_negative_id(self, test_client: AsyncClient, authenticated_user):
        """Тест получения пользователя с отрицательным ID."""
        # Устанавливаем cookies авторизованного пользователя
        test_client.cookies.update(authenticated_user)

        response = await test_client.get("/api/v1/users/-1")

        assert response.status_code == 404
        data = response.json()
        assert "Пользователь не найден" in data["detail"]

    @pytest.mark.asyncio
    async def test_get_users_pagination(self, test_client: AsyncClient):
        """Тест пагинации списка пользователей."""
        # Создаем несколько пользователей
        for i in range(5):
            user_data = {"username": f"user{i}", "email": f"user{i}@example.com", "password": "password123"}
            await test_client.post("/api/v1/auth/register", json=user_data)

        # Входим как первый пользователь
        login_data = {"username_or_email": "user0@example.com", "password": "password123"}
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)

        # Получаем список пользователей с пагинацией
        response = await test_client.get("/api/v1/users/?limit=3&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3  # Не больше лимита

    @pytest.mark.asyncio
    async def test_get_users_search(self, test_client: AsyncClient):
        """Тест поиска пользователей."""
        # Создаем пользователей с разными именами
        users_data = [
            {"username": "alice", "email": "alice@example.com", "password": "password123"},
            {"username": "bob", "email": "bob@example.com", "password": "password123"},
        ]

        for user_data in users_data:
            await test_client.post("/api/v1/auth/register", json=user_data)

        # Входим как первый пользователь
        login_data = {"username_or_email": "alice@example.com", "password": "password123"}
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)

        # Ищем пользователей по имени
        response = await test_client.get("/api/v1/users/?search=alice")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(user["username"] == "alice" for user in data)
