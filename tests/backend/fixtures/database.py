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
@pytest.mark.asyncio
async def test_db_engine() -> AsyncEngine:
    """
    Фикстура для создания тестового движка базы данных.
    Запускается один раз в начале сессии тестов.
    """
    print(f"{settings.MODE=}")
    print(f"{settings.DATABASE_URL=}")

    test_db_url = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/"
        "tg_web_app_test"
    )

    engine = create_async_engine(test_db_url, echo=False)

    # Возвращаем движок для использования в тестах
    yield engine

    # Очистка после завершения всех тестов
    await engine.dispose()



# Здесь будут дополнительные фикстуры:
# - clean_db (очистка БД между тестами)
# - create_tables (создание таблиц)
# - drop_tables (удаление таблиц)
