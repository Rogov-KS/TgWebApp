"""
Основные фикстуры для тестов бекенда
"""
import logging
from backend.entities.assemblers.models import *  # ruff: noqa: F401


# Отключаем логи Faker
logging.getLogger('faker.factory').setLevel(logging.WARNING)


# Импортируем фикстуры базы данных
from tests.backend.fixtures.database import (
    get_async_test_db_engine,
    get_async_test_db_session_maker,
    get_async_test_db_session,
)

# Импортируем фикстуры для тестовых данных
from tests.backend.fixtures.users import (
    get_user_dao,
    get_user_data,
    get_multiple_users_data,
    insert_test_user,
    insert_test_users,
)

from tests.backend.fixtures.game_sessions import (
    get_game_session_dao,
    get_game_session_data,
    get_multiple_game_sessions_data,
    insert_test_game_session,
    insert_test_game_sessions,
)

# Здесь будут основные фикстуры:
# - test_app (FastAPI приложение для тестов)
# - test_client (httpx.AsyncClient)
# - test_db (тестовая база данных)
# - test_redis (тестовый Redis)
# - test_celery (тестовый Celery)
