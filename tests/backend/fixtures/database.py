"""
Фикстуры для работы с базой данных в тестах
"""
import pytest
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from backend.core.config import get_settings


settings = get_settings(env_files=["envs/.env-base", "envs/.env-test"])


@pytest.fixture(scope="session")
def test_db_engine() -> int:
    """
    Фикстура для создания тестового движка базы данных.
    Запускается один раз в начале сессии тестов.
    """
    return 42


# Здесь будут дополнительные фикстуры:
# - clean_db (очистка БД между тестами)
# - create_tables (создание таблиц)
# - drop_tables (удаление таблиц)
