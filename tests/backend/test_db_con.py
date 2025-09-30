# tests/backend/test_db_connection.py
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.entities.user.dao import UserDAO


@pytest.mark.asyncio
async def test_db_connection(get_async_test_db_session: AsyncSession):
    """Тест подключения к БД"""
    # Создаем подключение к тестовой БД

    try:
        # Проверяем подключение
        result = await get_async_test_db_session.execute(text("SELECT 1 as test_value"))
        row = result.fetchone()
        assert row.test_value == 1

        # Читаем все таблицы
        result = await get_async_test_db_session.execute(text("SELECT version()"))
        row = result.fetchone()
        print(f"{row=}")

        # Созданные таблицы
        result = await get_async_test_db_session.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        )
        tables = result.fetchall()
        print(f"{tables=}")

        # Пользователи
        result = await get_async_test_db_session.execute(text("SELECT * FROM users"))
        users = result.fetchall()
        print("users:", *users, sep="\n")

        # Пользователи
        await get_async_test_db_session.execute(
            text("INSERT INTO users (username, is_admin, is_bot, is_active) VALUES ('John_3', false, false, true)")
        )
        await get_async_test_db_session.commit()

        # Создаем пользователя
        user_dao = UserDAO(get_async_test_db_session)
        user = await user_dao.create(username="John_4", is_admin=False, is_bot=False, is_active=True)
        print(f"Создан пользователь: {user}")

        result = await get_async_test_db_session.execute(text("SELECT * FROM users"))
        users = result.fetchall()
        print("users:", *users, sep="\n")

        print("✅ Подключение к БД успешно!")

    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        raise
