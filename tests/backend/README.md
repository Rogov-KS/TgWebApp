# Тесты для бекенда TgWebApp

## Структура тестов

```
tests/backend/
├── conftest.py                    # Основные фикстуры pytest
├── fixtures/                      # Дополнительные фикстуры
│   ├── database.py               # Фикстуры для БД
│   ├── auth.py                   # Фикстуры для аутентификации
│   ├── users.py                  # Фикстуры для пользователей
│   ├── game_sessions.py          # Фикстуры для игровых сессий
│   └── oauth.py                  # Фикстуры для OAuth
├── unit/                         # Unit тесты
│   ├── entities/
│   │   ├── user/                 # Тесты для пользователей
│   │   ├── game_session/         # Тесты для игровых сессий
│   │   └── auth/                 # Тесты для аутентификации
│   └── core/                     # Тесты для core модулей
├── integration/                  # Интеграционные тесты
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_game_sessions.py
│   ├── test_leaderboard.py
│   └── test_oauth.py
└── e2e/                         # End-to-end тесты
    ├── test_auth_flow.py
    └── test_game_flow.py
```

## Запуск тестов

### Установка зависимостей
```bash
# Установка с dev зависимостями (включая тестовые)
uv add --dev pytest pytest-asyncio pytest-cov pytest-mock pytest-env factory-boy faker testcontainers aioredis

# Или установка только тестовых зависимостей
uv add --dev pytest pytest-asyncio pytest-cov pytest-mock pytest-env factory-boy faker testcontainers aioredis
```

### Запуск всех тестов
```bash
uv run pytest
```

### Запуск по категориям
```bash
# Unit тесты
uv run pytest -m unit

# Интеграционные тесты
uv run pytest -m integration

# E2E тесты
uv run pytest -m e2e

# Тесты аутентификации
uv run pytest -m auth

# Тесты OAuth
uv run pytest -m oauth
```

### Запуск с покрытием
```bash
uv run pytest --cov=backend --cov-report=html
```

## Настройка окружения

1. Скопируйте `test.env.example` в `test.env`
2. Настройте тестовую базу данных
3. Настройте тестовый Redis
4. Установите переменные окружения для тестов

## Фикстуры

### Основные фикстуры (conftest.py)
- `test_app` - FastAPI приложение для тестов
- `test_client` - httpx.AsyncClient
- `test_db` - тестовая база данных
- `test_redis` - тестовый Redis
- `test_celery` - тестовый Celery

### Специфические фикстуры
- `database.py` - фикстуры для работы с БД
- `auth.py` - фикстуры для аутентификации
- `users.py` - фикстуры для пользователей
- `game_sessions.py` - фикстуры для игровых сессий
- `oauth.py` - фикстуры для OAuth

## Маркеры тестов

- `@pytest.mark.unit` - Unit тесты
- `@pytest.mark.integration` - Интеграционные тесты
- `@pytest.mark.e2e` - End-to-end тесты
- `@pytest.mark.slow` - Медленные тесты
- `@pytest.mark.auth` - Тесты аутентификации
- `@pytest.mark.oauth` - Тесты OAuth
- `@pytest.mark.database` - Тесты базы данных
- `@pytest.mark.redis` - Тесты Redis
- `@pytest.mark.celery` - Тесты Celery


## EventLoop с асинхронными фикстурами и тестами

- в итоге поставил `asyncio_default_test_loop_scope = session` - а это означает что у всех тестов один event_loop, а это означает что один зависший тест может потянуть и остальные
- мб от этого стоит отказаться
