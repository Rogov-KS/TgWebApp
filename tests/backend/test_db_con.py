# tests/backend/test_db_connection.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


@pytest.mark.asyncio
async def test_db_connection(test_db_session: AsyncSession):
    """Тест подключения к БД"""
    # Создаем подключение к тестовой БД

    try:
        # Проверяем подключение
        result = await test_db_session.execute(text("SELECT 1 as test_value"))
        row = result.fetchone()
        assert row.test_value == 1

        # Читаем все таблицы
        result = await test_db_session.execute(text("SELECT version()"))
        row = result.fetchone()
        print(f"{row=}")

        # Созданные таблицы
        result = await test_db_session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"))
        tables = result.fetchall()
        print(f"{tables=}")

        # Пользователи
        result = await test_db_session.execute(text("SELECT * FROM users"))
        users = result.fetchall()
        print(f"{users=}")

        print("✅ Подключение к БД успешно!")

    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        raise
