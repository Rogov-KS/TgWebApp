"""
Фикстуры для работы с базой данных в тестах
"""
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from backend.core.config import get_settings
from backend.core.database import Base


settings = get_settings(env_files=["envs/.env-base", "envs/.env-test"])


@pytest_asyncio.fixture(scope="session")
async def test_db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Фикстура для создания тестового движка базы данных.
    Запускается один раз в начале сессии тестов.
    """
    import asyncio
    current_loop = asyncio.get_running_loop()
    print(f"Current event loop (async def test_db_engine): {current_loop}")
    print(f"{settings.MODE=}")
    assert settings.MODE == "TEST"
    test_db_url = settings.DATABASE_URL

    engine = create_async_engine(test_db_url, echo=False)

    # Создаем все таблицы в начале сессии
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Все таблицы созданы успешно")

    yield engine

    # Удаляем все таблицы в конце сессии
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("🗑️ Все таблицы удалены успешно")

    await engine.dispose()

@pytest_asyncio.fixture(scope="session")
async def test_db_session_maker(test_db_engine: AsyncEngine) -> async_sessionmaker:
    """
    Фикстура для создания тестового движка базы данных.
    Запускается один раз в начале сессии тестов.
    """
    import asyncio
    current_loop = asyncio.get_running_loop()
    print(f"Current event loop (async def test_db_session): {current_loop}")
    session_maker = async_sessionmaker(test_db_engine, expire_on_commit=False)
    return session_maker

@pytest_asyncio.fixture
async def test_db_session(test_db_session_maker: async_sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    """
    Фикстура для создания сессии БД для каждого теста.
    Автоматически создает и закрывает сессию для каждого теста.
    """
    import asyncio
    current_loop = asyncio.get_running_loop()
    print(f"Current event loop (async def test_db_session): {current_loop}")
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
