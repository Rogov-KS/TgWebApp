"""
Основные фикстуры для тестов бекенда
"""
import logging
from backend.entities.assemblers.models import *


# Отключаем логи Faker
logging.getLogger('faker.factory').setLevel(logging.WARNING)


# Импортируем фикстуры базы данных
# ruff: noqa: F401
from tests.backend.fixtures.database import (
    test_db_engine,
    test_db_session_maker,
    test_db_session,
)

# Импортируем фикстуры для тестовых данных
# ruff: noqa: F401
from tests.backend.fixtures.users import (
    user_data,
    multiple_users_data,
    test_user,
    test_users,
)

# ruff: noqa: F401
from tests.backend.fixtures.game_sessions import (
    game_session_data,
    multiple_game_sessions_data,
    test_game_session,
    test_game_sessions,
)

# Здесь будут основные фикстуры:
# - test_app (FastAPI приложение для тестов)
# - test_client (httpx.AsyncClient)
# - test_db (тестовая база данных)
# - test_redis (тестовый Redis)
# - test_celery (тестовый Celery)
