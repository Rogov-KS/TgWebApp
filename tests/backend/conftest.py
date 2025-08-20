"""
Основные фикстуры для тестов бекенда
"""

# Импортируем фикстуры базы данных
from tests.backend.fixtures.database import (
    test_db_engine,
    test_db_session_maker,
    test_db_session,
)

# Здесь будут основные фикстуры:
# - test_app (FastAPI приложение для тестов)
# - test_client (httpx.AsyncClient)
# - test_db (тестовая база данных)
# - test_redis (тестовый Redis)
# - test_celery (тестовый Celery)
