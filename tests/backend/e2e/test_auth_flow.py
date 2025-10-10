"""E2E тесты для полного flow авторизации."""

from httpx import AsyncClient
import pytest


class TestAuthFlow:
    """Тесты для полного flow авторизации."""

    @pytest.mark.asyncio
    async def test_complete_auth_flow_email_password(self, test_client: AsyncClient):
        """Тест полного flow авторизации через email/password."""
        # 1. Регистрация пользователя
        user_data = {"username": "testuser", "email": "test@example.com", "password": "password123"}

        register_response = await test_client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 200

        register_data = register_response.json()
        assert register_data["username"] == "testuser"
        assert register_data["email"] == "test@example.com"
        assert register_data["is_active"] is True
        assert register_data["is_admin"] is False

        # 2. Вход пользователя
        login_data = {"username_or_email": "test@example.com", "password": "password123"}

        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200

        login_result = login_response.json()
        assert "access_token" in login_result
        assert "refresh_token" in login_result

        # Проверяем что cookies установлены
        assert "access_token" in login_response.cookies
        assert "refresh_token" in login_response.cookies

        # 3. Получение профиля пользователя
        test_client.cookies.update(login_response.cookies)

        profile_response = await test_client.get("/api/v1/users/me")
        assert profile_response.status_code == 200

        profile_data = profile_response.json()
        assert profile_data["username"] == "testuser"
        assert profile_data["email"] == "test@example.com"
        assert profile_data["id"] == register_data["id"]

        # 4. Обновление токена
        refresh_response = await test_client.post("/api/v1/auth/refresh")
        assert refresh_response.status_code == 200

        refresh_result = refresh_response.json()
        assert "access_token" in refresh_result
        assert "refresh_token" in refresh_result

        # Проверяем что новые cookies установлены
        assert "access_token" in refresh_response.cookies
        assert "refresh_token" in refresh_response.cookies

        # 5. Проверяем что новый токен работает
        test_client.cookies.update(refresh_response.cookies)

        profile_response_after_refresh = await test_client.get("/api/v1/users/me")
        assert profile_response_after_refresh.status_code == 200

        # 6. Выход пользователя
        logout_response = await test_client.post("/api/v1/auth/logout")
        assert logout_response.status_code == 200

        logout_result = logout_response.json()
        assert logout_result["message"] == "Выход выполнен успешно"

        # 7. Проверяем что после выхода доступ к защищенным ресурсам запрещен
        protected_response = await test_client.get("/api/v1/users/me")
        assert protected_response.status_code == 401

    @pytest.mark.asyncio
    async def test_complete_auth_flow_username_password(self, test_client: AsyncClient):
        """Тест полного flow авторизации через username/password."""
        # 1. Регистрация пользователя
        user_data = {"username": "testuser", "email": "test@example.com", "password": "password123"}

        register_response = await test_client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 200

        # 2. Вход по username
        login_data = {"username_or_email": "testuser", "password": "password123"}

        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200

        # 3. Проверяем доступ к защищенным ресурсам
        test_client.cookies.update(login_response.cookies)

        profile_response = await test_client.get("/api/v1/users/me")
        assert profile_response.status_code == 200

        profile_data = profile_response.json()
        assert profile_data["username"] == "testuser"

    @pytest.mark.asyncio
    async def test_complete_telegram_auth_flow(self, test_client: AsyncClient):
        """Тест полного flow авторизации через Telegram."""
        from unittest.mock import patch

        valid_telegram_init_data = (
            "user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22John%22%2C"
            "%22last_name%22%3A%22Doe%22%2C%22username%22%3A%22johndoe%22%2C"
            "%22language_code%22%3A%22en%22%7D&"
            "auth_date=1640995200&"
            "hash=test_hash_123"
        )

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

            # 1. Авторизация через Telegram
            auth_data = {"init_data": valid_telegram_init_data}

            telegram_response = await test_client.post("/api/v1/auth/telegram/", json=auth_data)
            assert telegram_response.status_code == 200

            telegram_result = telegram_response.json()
            assert "access_token" in telegram_result
            assert "refresh_token" in telegram_result

            # Проверяем что cookies установлены
            assert "access_token" in telegram_response.cookies
            assert "refresh_token" in telegram_response.cookies

            # 2. Получение профиля пользователя
            test_client.cookies.update(telegram_response.cookies)

            profile_response = await test_client.get("/api/v1/users/me")
            assert profile_response.status_code == 200

            profile_data = profile_response.json()
            assert profile_data["username"] == "johndoe"
            assert profile_data["telegram_id"] == 123456789

            # 3. Обновление токена
            refresh_response = await test_client.post("/api/v1/auth/refresh")
            assert refresh_response.status_code == 200

            # 4. Выход пользователя
            logout_response = await test_client.post("/api/v1/auth/logout")
            assert logout_response.status_code == 200

            # 5. Проверяем что после выхода доступ запрещен
            protected_response = await test_client.get("/api/v1/users/me")
            assert protected_response.status_code == 401

    @pytest.mark.asyncio
    async def test_auth_flow_with_multiple_sessions(self, test_client: AsyncClient):
        """Тест flow с несколькими сессиями."""
        # 1. Регистрируем пользователя
        user_data = {"username": "testuser", "email": "test@example.com", "password": "password123"}

        register_response = await test_client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 200

        # 2. Входим первый раз
        login_data = {"username_or_email": "test@example.com", "password": "password123"}

        login_response_1 = await test_client.post("/api/v1/auth/login", json=login_data)
        assert login_response_1.status_code == 200

        # 3. Входим второй раз (должен создать новую сессию)
        login_response_2 = await test_client.post("/api/v1/auth/login", json=login_data)
        assert login_response_2.status_code == 200

        # 4. Проверяем что оба токена работают
        test_client.cookies.update(login_response_1.cookies)
        profile_response_1 = await test_client.get("/api/v1/users/me")
        assert profile_response_1.status_code == 200

        test_client.cookies.update(login_response_2.cookies)
        profile_response_2 = await test_client.get("/api/v1/users/me")
        assert profile_response_2.status_code == 200

        # 5. Выходим из одной сессии
        logout_response = await test_client.post("/api/v1/auth/logout")
        assert logout_response.status_code == 200

        # 6. Проверяем что доступ все еще есть (другая сессия активна)
        # Но текущие cookies недействительны
        protected_response = await test_client.get("/api/v1/users/me")
        assert protected_response.status_code == 401

    @pytest.mark.asyncio
    async def test_auth_flow_token_expiration(self, test_client: AsyncClient):
        """Тест flow с истечением токена."""
        # 1. Регистрируем и входим
        user_data = {"username": "testuser", "email": "test@example.com", "password": "password123"}

        await test_client.post("/api/v1/auth/register", json=user_data)

        login_data = {"username_or_email": "test@example.com", "password": "password123"}

        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200

        # 2. Проверяем доступ
        test_client.cookies.update(login_response.cookies)
        profile_response = await test_client.get("/api/v1/users/me")
        assert profile_response.status_code == 200

        # 3. Симулируем истечение токена (устанавливаем невалидный токен)
        test_client.cookies.set("access_token", "invalid_token")

        # 4. Проверяем что доступ запрещен
        protected_response = await test_client.get("/api/v1/users/me")
        assert protected_response.status_code == 401

        # 5. Обновляем токен
        test_client.cookies.set("refresh_token", login_response.cookies.get("refresh_token"))
        refresh_response = await test_client.post("/api/v1/auth/refresh")
        assert refresh_response.status_code == 200

        # 6. Проверяем что доступ восстановлен
        test_client.cookies.update(refresh_response.cookies)
        profile_response_after_refresh = await test_client.get("/api/v1/users/me")
        assert profile_response_after_refresh.status_code == 200

    @pytest.mark.asyncio
    async def test_auth_flow_concurrent_sessions(self, test_client: AsyncClient):
        """Тест concurrent сессий."""
        # 1. Регистрируем пользователя
        user_data = {"username": "testuser", "email": "test@example.com", "password": "password123"}

        await test_client.post("/api/v1/auth/register", json=user_data)

        # 2. Создаем несколько сессий одновременно
        login_data = {"username_or_email": "test@example.com", "password": "password123"}

        # Создаем несколько клиентов для симуляции concurrent запросов
        from httpx import AsyncClient as AsyncClientClass

        async with AsyncClientClass(app=test_client._transport.app, base_url=test_client.base_url) as client1:
            async with AsyncClientClass(app=test_client._transport.app, base_url=test_client.base_url) as client2:
                # Входим в двух разных сессиях
                login_response_1 = await client1.post("/api/v1/auth/login", json=login_data)
                login_response_2 = await client2.post("/api/v1/auth/login", json=login_data)

                assert login_response_1.status_code == 200
                assert login_response_2.status_code == 200

                # Проверяем что обе сессии работают
                client1.cookies.update(login_response_1.cookies)
                client2.cookies.update(login_response_2.cookies)

                profile_response_1 = await client1.get("/api/v1/users/me")
                profile_response_2 = await client2.get("/api/v1/users/me")

                assert profile_response_1.status_code == 200
                assert profile_response_2.status_code == 200

                # Проверяем что это один и тот же пользователь
                profile_data_1 = profile_response_1.json()
                profile_data_2 = profile_response_2.json()

                assert profile_data_1["id"] == profile_data_2["id"]
                assert profile_data_1["username"] == profile_data_2["username"]
