"""
Основные фикстуры для тестов бекенда
"""

import asyncio
from collections.abc import AsyncGenerator
import logging

from fastapi import FastAPI
from httpx import AsyncClient
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import get_settings
from backend.core.database import get_async_session
from backend.entities.assemblers.models import *  # ruff: noqa: F401
from backend.main import app

# Отключаем логи Faker
logging.getLogger("faker.factory").setLevel(logging.WARNING)

# Настройка для pytest-asyncio
pytest_asyncio.asyncio_default_test_loop_scope = "session"

# Импортируем фикстуры базы данных

# Импортируем фикстуры для тестовых данных


@pytest_asyncio.fixture(scope="session")
async def test_app() -> AsyncGenerator[FastAPI, None]:
    """
    Фикстура для создания тестового FastAPI приложения.
    Создается один раз для всей сессии тестов.
    """
    # Настраиваем тестовое окружение
    settings = get_settings(env_files=["configs/envs/.env-base", "configs/envs/.env-test"])

    # Переопределяем зависимости для тестов
    async def override_get_db():
        # Здесь будет использоваться тестовая БД
        pass

    app.dependency_overrides[get_async_session] = override_get_db

    yield app

    # Очищаем переопределения после тестов
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """
    Фикстура для создания тестового HTTP клиента.
    Создается для каждого теста.
    """
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def test_db_session(get_async_test_db_session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """
    Фикстура для получения тестовой сессии БД.
    Создается для каждого теста.
    """
    yield get_async_test_db_session


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """
    Фикстура для создания event loop для всей сессии тестов.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
