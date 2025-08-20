# tests/backend/test_db_connection.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from backend.core.config import get_settings

settings = get_settings(env_files=["envs/.env-base", "envs/.env-test"])


@pytest.mark.asyncio
async def test_db_connection():
    """Тест подключения к БД"""
    # Создаем подключение к тестовой БД
    # Замените параметры на ваши реальные данные
    print()
    print(f"{settings.MODE=}")
    print(f"{settings.DATABASE_URL=}")
    test_db_url = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/"
        "tg_web_app_test"
    )

    engine = create_async_engine(test_db_url, echo=False)

    try:
        # Проверяем подключение
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1 as test_value"))
            row = result.fetchone()
            assert row.test_value == 1

        print("✅ Подключение к БД успешно!")

    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        raise
    finally:
        await engine.dispose()
