"""
Фикстуры для работы с базой данных в тестах
"""

from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.core.config import get_settings
from backend.core.database import Base

settings = get_settings(env_files=["configs/envs/.env-base", "configs/envs/.env-test"])


async def create_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()
        print("✅ Все таблицы созданы успешно")


async def truncate_tables(engine: AsyncEngine):
    """
    Очищает все таблицы в правильном порядке с учетом внешних ключей.
    Сначала удаляем данные из таблиц с внешними ключами,
    затем из основных таблиц.
    """
    async with engine.begin() as conn:
        # Получаем все таблицы из метаданных
        tables = Base.metadata.tables.values()

        # Очищаем все таблицы
        for table in tables:
            try:
                await conn.execute(text(f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE;"))
            except Exception as e:
                print(f"Ошибка при очистке таблицы {table.name}: {e}")

        await conn.commit()
        print("🗑️ Все таблицы очищены успешно")


async def drop_tables(engine: AsyncEngine) -> None:
    try:
        async with engine.begin() as conn:
            # Получаем все таблицы из метаданных
            tables = Base.metadata.tables.values()

            # Очищаем все таблицы
            for table in tables:
                try:
                    await conn.execute(text(f"DROP TABLE {table.name} CASCADE;"))
                except Exception as e:
                    print(f"Ошибка при удалении таблицы {table.name}: {e}")
            print("🗑️ Все таблицы удалены успешно")
    except Exception as e:
        print(f"Ошибка при удалении таблиц: {e}")


async def start_up_db_tables(engine: AsyncEngine) -> None:
    # await drop_tables(engine)
    await create_tables(engine)
    await truncate_tables(engine)
    print("💾 STARTUP-ed - FROM MAIN CONFTEST")


async def tear_down_db_tables(engine: AsyncEngine) -> None:
    await truncate_tables(engine)
    await drop_tables(engine)
    await engine.dispose()


@pytest_asyncio.fixture
async def get_async_test_db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Фикстура для создания тестового движка базы данных.
    Запускается один раз в начале сессии тестов.
    """
    msg = "Settings.MODE must be equal to 'TEST' for tests with database"
    assert settings.MODE == "TEST", msg
    test_db_url = settings.DATABASE_URL

    engine = create_async_engine(test_db_url, echo=False)

    await start_up_db_tables(engine)

    try:
        yield engine
    finally:
        await tear_down_db_tables(engine)


@pytest_asyncio.fixture
async def get_async_test_db_session_maker(
    get_async_test_db_engine: AsyncEngine,
) -> AsyncGenerator[async_sessionmaker, None]:
    """
    Фикстура для создания тестового движка базы данных.
    Запускается один раз в начале сессии тестов.
    """
    session_maker = async_sessionmaker(get_async_test_db_engine, expire_on_commit=False)
    return session_maker


@pytest_asyncio.fixture
async def get_async_test_db_session(
    get_async_test_db_session_maker: async_sessionmaker,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Фикстура для создания сессии БД для каждого теста.
    Автоматически создает и закрывает сессию для каждого теста.
    """
    async with get_async_test_db_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


# Здесь будут дополнительные фикстуры:
# - clean_db (очистка БД между тестами)
# - create_tables (создание таблиц)
# - drop_tables (удаление таблиц)
