"""
Фикстуры для работы с базой данных в тестах
"""
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from backend.core.config import get_settings


settings = get_settings(env_files=["envs/.env-base", "envs/.env-test"])


@pytest_asyncio.fixture(scope="session")
async def test_db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Фикстура для создания тестового движка базы данных.
    Запускается один раз в начале сессии тестов.
    """
    print(f"{settings.DATABASE_URL=}")
    test_db_url = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/"
        "tg_web_app_test"
    )

    engine = create_async_engine(test_db_url, echo=False)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
def test_db_session_maker(test_db_engine: AsyncEngine) -> AsyncGenerator[async_sessionmaker, None]:
    session_maker = async_sessionmaker(test_db_engine, expire_on_commit=False)
    yield session_maker


@pytest_asyncio.fixture
async def test_db_session(test_db_session_maker: async_sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    """
    Фикстура для создания сессии БД для каждого теста.
    Автоматически создает и закрывает сессию для каждого теста.
    """
    async with test_db_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise

# Здесь будут дополнительные фикстуры:
# - clean_db (очистка БД между тестами)
# - create_tables (создание таблиц)
# - drop_tables (удаление таблиц)
